import logging
import re

from django.db.models import Q
from rest_framework.exceptions import ValidationError

logger = logging.getLogger()


class DuplicatedRecord(ValidationError):
    def __init__(self, serializer, integrity_error):
        self.integrity_error = integrity_error
        self.model = serializer.Meta.model if not hasattr(serializer, "child") else serializer.child.Meta.model
        self.data = serializer.initial_data
        self.engine = self._get_engine(integrity_error=self.integrity_error)
        self.constraints, self.values = self._parse_error()

        message = (
            f"Duplicate key constraint raised for {self.integrity_error}. "
            "Try adding a UniqueTogetherValidator to the serializer"
        )
        super().__init__(message)

    @classmethod
    def verify(cls, integrity_error):
        return cls._get_engine(integrity_error=integrity_error) is not None

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

    @classmethod
    def _get_engine(cls, integrity_error):
        known_messages = {
            "psql": "duplicate key value violates unique",
            "sqlite": "UNIQUE constraint failed",
        }

        error = str(integrity_error)
        for engine, message in known_messages.items():
            if message in error:
                return engine
        return None

    def _parse_error(self):
        parser = getattr(self, f"_parse_{self.engine}")
        return parser()

    def get_params(self):
        return dict(zip(self.constraints, self.values))

    def get_filter(self):
        return Q(**self.get_params())

    def get_object(self):
        return self.model.objects.get(self.get_filter())


class UpdatingSoftDeletedException(Exception):
    def __init__(self):
        message = "It's not possible to save changes to a soft deleted model. Undelete it first."
        super().__init__(message)
