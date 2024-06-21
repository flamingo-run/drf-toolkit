import abc
import logging
import re
from collections.abc import Iterable
from typing import Any

from django.core.exceptions import ValidationError
from django.db import connections
from django.db.models import Model, Q
from django.db.utils import IntegrityError
from rest_framework import response, status, views

logger = logging.getLogger()


class DatabaseIntegrityError(ValidationError, abc.ABC):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, model_klass, body, integrity_error):
        self.integrity_error = integrity_error
        self.model = model_klass
        self.data = body
        self.engine = connections["default"].vendor
        self.outcome = self.process()
        message = self.build_message()
        super().__init__(message=message, code=self.status_code)

    @abc.abstractmethod
    def build_message(self) -> str: ...  # fmt: skip

    @abc.abstractmethod
    def _parse_psql(self): ...  # fmt: skip

    @abc.abstractmethod
    def _parse_sqlite(self): ...  # fmt: skip

    @classmethod
    @abc.abstractmethod
    def verify(cls, integrity_error: IntegrityError) -> bool: ...  # fmt: skip

    @property
    def response(self):
        return response.Response(data={"errors": self.message}, status=self.code, exception=self)

    def process(self):
        match self.engine:
            case "sqlite":
                return self._parse_sqlite()
            case "postgresql":
                return self._parse_psql()
        raise TypeError(f"Unknown database engine {self.engine}")


class DuplicatedRecord(DatabaseIntegrityError):
    status_code = status.HTTP_409_CONFLICT

    @property
    def constraints(self) -> tuple[str]:
        return self.outcome[0]

    @property
    def values(self) -> tuple[Any]:
        return self.outcome[1]

    @classmethod
    def verify(cls, integrity_error: IntegrityError) -> bool:
        return "UNIQUE constraint failed" in str(integrity_error) or "duplicate key value violates unique" in str(
            integrity_error,
        )

    def build_message(self) -> str:
        model_name = self.model.__name__
        violation = " and ".join([f"{constraint}={value}" for constraint, value in zip(self.constraints, self.values)])
        return f"A {model_name} with `{violation}` already exists."

    def get_params(self) -> dict[str, Any]:
        return dict(zip(self.constraints, self.values))

    def get_filter(self) -> Q:
        return Q(**self.get_params())

    def get_object(self) -> Model:
        return self.model.objects.get(self.get_filter())

    def _parse_psql(self):
        # Parse SQL-provided error output for constraint failures, such as:
        # 'duplicate key value violates unique constraint "<name>"
        # DETAIL:  Key (<field>)=(<value>) already exists.'
        # and also for multi-valued constraints such as:
        # 'duplicate key value violates unique constraint "<name>"
        # DETAIL:  Key (<field_a>, <field_b>)=(<value_a>,<value_b>) already exists.'
        error_detail = self.integrity_error.args[0].splitlines()[-1]
        parsed = re.search(r"Key \((?P<keys>.*)\)=\((?P<values>.*)\)", error_detail)

        def _clean(name):
            try:
                return [item.strip() for item in parsed.group(name).split(",")]
            except AttributeError:
                logger.warning(f"Unable to detect constraints for error: {name}")
                return []

        return _clean("keys"), _clean("values")

    def _parse_sqlite(self):
        error_detail = self.integrity_error.args[0].split(":")[-1].strip()
        keys = [item.split(".")[-1] for item in error_detail.split(",")]
        values = [self.data[key] for key in keys]
        return keys, values


class InvalidRecord(DatabaseIntegrityError):
    def build_message(self) -> str:
        model_name = self.model.__name__
        name = self.outcome
        check = self.constraint_check or ""
        return f"This {model_name} violates the check `{name}` which states `{check!s}`"

    @property
    def constraint_check(self) -> Q | None:
        for constraint in self.model._meta.constraints:
            if constraint.name == self.outcome:
                return constraint.check
        return None

    def _parse_psql(self):
        error_detail = self.integrity_error.args[0].splitlines()[0]
        parsed = re.search(r"violates check constraint \"(?P<name>.*)\"", error_detail)
        return parsed.group("name")

    def _parse_sqlite(self):
        constraint_name = self.integrity_error.args[0].split(":")[-1].strip()
        return constraint_name

    @classmethod
    def verify(cls, integrity_error: IntegrityError) -> bool:
        return "CHECK constraint failed" in str(integrity_error) or "violates check constraint" in str(integrity_error)


class ConflictException(ValidationError):
    status_code = status.HTTP_409_CONFLICT

    def __init__(self, with_models: Iterable[Model], message: str | None = None):
        self.with_models = list(with_models)
        message = message or self.build_message()
        super().__init__(message=message, code=self.status_code)

    def build_message(self) -> str:
        return f"Model is duplicated with {' | '.join([str(model) for model in self.with_models])}"


class ExclusionDuplicatedRecord(DuplicatedRecord):
    def build_message(self) -> str:
        model_name = self.model.__name__
        return f"This {model_name} violates exclusion constraint `{self.constraint_name}`"

    def _parse_psql(self):
        error_detail = self.integrity_error.args[0].splitlines()[0]
        parsed = re.search(r"violates exclusion constraint \"(?P<name>.*)\"", error_detail)
        constraint_name = parsed.group("name")

        error_detail = self.integrity_error.args[0].splitlines()[1].split("conflicts with existing key")[-1].strip()
        keys_str = error_detail.split("=")[0][1:-1]
        values_str = error_detail.split("=")[1][1:-2]

        keys = [key.strip() for key in keys_str.split(",")]
        csv_regex = re.compile(
            r"""
            (                  # Start capturing here.
              [\d\w\s]+?         # Either a series of non-comma non-quote characters.
              |                # OR
              [\[\(](.*)[\]\)]
            )                  # Done capturing.
            \s*                # Allow arbitrary space before the comma.
            (?:,|$)            # Followed by a comma or the end of a string.
            """,
            re.VERBOSE,
        )

        def _clean(v):
            v = v.strip()
            if v == "":
                return None
            return v

        values = []
        for match in csv_regex.findall(values_str):
            value = _clean(match[0])
            if value.startswith("(") or value.startswith("["):
                value = [_clean(item) for item in value[1:-1].split(",")]
            values.append(value)
        return keys, values, constraint_name

    def _parse_sqlite(self): ...

    @classmethod
    def verify(cls, integrity_error: IntegrityError) -> bool:
        return "violates exclusion constraint" in str(integrity_error)

    @property
    def constraint_name(self):
        return self.outcome[2]


class UpdatingSoftDeletedException(Exception):
    def __init__(self):
        message = "It's not possible to save changes to a soft deleted model. Undelete it first."
        super().__init__(message)


def custom_exception_handler(exc, context):
    resp = views.exception_handler(exc, context)
    if resp is None:
        if isinstance(exc, ValidationError):
            msg = getattr(exc, "message", exc.args[0])
            data = msg if isinstance(msg, dict | str) else exc.messages

            status_code = getattr(exc, "code", "") or status.HTTP_400_BAD_REQUEST
            return response.Response(data={"errors": data}, status=status_code, exception=exc)
        if isinstance(exc, IntegrityError):
            if DuplicatedRecord.verify(exc):
                error = DuplicatedRecord(
                    model_klass=context["view"].get_queryset().model,
                    body=context["request"].data,
                    integrity_error=exc,
                )
                return error.response
            if InvalidRecord.verify(exc):
                error = InvalidRecord(
                    model_klass=context["view"].get_queryset().model,
                    body=context["request"].data,
                    integrity_error=exc,
                )
                return error.response
            if ExclusionDuplicatedRecord.verify(exc):
                error = ExclusionDuplicatedRecord(
                    model_klass=context["view"].get_queryset().model,
                    body=context["request"].data,
                    integrity_error=exc,
                )
                return error.response
    return resp
