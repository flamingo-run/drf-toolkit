# pylint: disable=invalid-name
import inspect
import os
import re
from contextlib import contextmanager
from io import StringIO
from typing import Optional, Callable, Union, Type, Dict, List, Any
from unittest.mock import patch, ANY

from django.core.cache import cache
from django.core.management import call_command
from django.utils.connection import ConnectionProxy
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APITransactionTestCase


class BaseApiTest(APITransactionTestCase):
    maxDiff = None

    def setUp(self):
        super().setUp()
        cache.clear()

    def real_cache(self):
        return self.settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}})

    def assertNoPendingMigration(self, app_name):  # pylint: disable=invalid-name
        out = StringIO()
        message = None
        try:
            call_command("makemigrations", app_name, "--check", "--dry-run", interactive=False, stdout=out)
        except SystemExit:
            message = f"Missing migration. Run python manage.py makemigrations {app_name}"
        self.assertIn("No changes", out.getvalue(), msg=message)

    def uuid_file_path_regex(self, prefix, pk, name, extension):
        uuid_regex = r"[0-9a-f]{8}\-[0-9a-f]{4}\-4[0-9a-f]{3}\-[89ab][0-9a-f]{3}\-[0-9a-f]{12}"
        return re.compile(rf"^{prefix}/{pk}/{name}_{uuid_regex}\.{extension}$")

    def assertUUIDFilePath(self, prefix, name, extension, pk, file):  # pylint: disable=invalid-name
        pattern = self.uuid_file_path_regex(prefix=prefix, pk=pk, name=name, extension=extension)
        self.assertTrue(pattern.match(str(file)))

    def assertResponseList(self, expected_items: List[Dict], response, response_key: str = "results"):
        self.assertResponse(
            expected_status=status.HTTP_200_OK,
            expected_body=expected_items,
            response=response,
            response_key=response_key,
        )

    def assertResponseDetail(self, expected_item: Dict, response):
        self.assertResponse(
            expected_status=status.HTTP_200_OK,
            expected_body=expected_item,
            response=response,
            response_key=None,
        )

    def assertResponseCreate(self, expected_item, response):
        self.assertResponse(
            expected_status=status.HTTP_201_CREATED,
            expected_body=expected_item,
            response=response,
            response_key=None,
        )

    def assertResponseUpdated(self, expected_item, response):
        self.assertResponse(
            expected_status=status.HTTP_200_OK,
            expected_body=expected_item,
            response=response,
            response_key=None,
        )

    def assertResponseDeleted(self, response):
        self.assertResponse(
            expected_status=status.HTTP_204_NO_CONTENT,
            expected_body="",
            response=response,
            response_key=None,
        )

    def assertResponseNotAllowed(self, response):
        method = response.request["REQUEST_METHOD"]
        expected = {"detail": f'Method "{method}" not allowed.'}
        self.assertResponse(
            expected_status=status.HTTP_405_METHOD_NOT_ALLOWED,
            expected_body=expected,
            response=response,
            response_key=None,
        )

    def assertResponse(
        self,
        expected_status: int,
        response: Response,
        expected_body: Optional[Any] = None,
        response_key: Optional[str] = None,
    ):
        response_content = (
            response.json() if response.headers.get("Content-Type") == "application/json" else response.content.decode()
        )
        msg = f"Expected status code {expected_status}, but received {response.status_code} with {response_content}"
        self.assertEqual(expected_status, response.status_code, msg)

        if expected_body is not None:
            if response_key:
                body = response_content[response_key]
            else:
                body = response_content
            self.assertResponseMatch(expected=expected_body, received=body)
        else:
            msg = f"Expected body to be empty, but received {response_content}"
            self.assertEqual(expected_body, response.content.decode(), msg)

    def assertResponseMatch(self, expected, received):  # pylint: disable=invalid-name
        def _assert_dict(expected_item, received_item, idx=None):
            msg = f"At item #{idx}:: " if idx else ""
            if expected_item == received_item:
                return {}

            expected_keys = set(expected_item)
            received_keys = set(received_item)
            if expected_keys != received_keys:
                missing_keys = expected_keys - received_keys
                if missing_keys:
                    msg += f"There's {len(missing_keys)} fields missing: {' | '.join(missing_keys)}"
                    return {"__len__": msg}

                extra_keys = received_keys - expected_keys
                if extra_keys:
                    msg += f"There's {len(extra_keys)} unexpected fields: {' | '.join(extra_keys)}"
                    return {"__keys__": msg}

            errors = {}
            for key in expected_item:
                inner_errors = _compare(expected_item=expected_item[key], received_item=received_item[key])
                for inner_key, inner_error in inner_errors.items():
                    inner_key_str = f".{inner_key}" if not inner_key.startswith("__") else ""
                    errors[f"{key}{inner_key_str}"] = inner_error

            return errors

        def _compare(expected_item, received_item):
            if expected_item is ANY:
                return {}

            if isinstance(expected_item, re.Pattern):
                if not expected_item.match(received_item):
                    msg = f"Received `{received_item}`, but expected to match `{expected_item.pattern}`"
                    return {"__match__": msg}
                return {}

            if isinstance(expected_item, list):
                if not isinstance(received_item, (list, set)):
                    msg = f"Received `{received_item}`, but expected to `{expected_item}`"
                    return {"__match__": msg}

                if len(expected_item) != len(received_item):
                    msg = f"Received {len(received_item)} items and it was expected to have {len(expected_item)}"
                    return {"__len__": msg}

                all_errors = {}
                for _idx, (_expected_item, _received_item) in enumerate(zip(expected_item, received_item)):
                    inner_errors = _compare(expected_item=_expected_item, received_item=_received_item)
                    for inner_key, inner_error in inner_errors.items():
                        all_errors[f"[#{_idx}] {inner_key}"] = inner_error
                return all_errors

            if isinstance(expected_item, dict) and isinstance(received_item, dict):
                return _assert_dict(expected_item=expected_item, received_item=received_item)

            if isinstance(expected_item, set):
                if not isinstance(received_item, list):
                    msg = (
                        f"Received `{received_item}`, "
                        f"but expected to have `{', '.join(sorted(expected_item))}` items"
                    )
                    return {"__eq__": msg}
                try:
                    self.assertEqual(expected_item, set(received_item))
                    return {}
                except AssertionError:
                    msg = (
                        f"Received `{', '.join(sorted(received_item))}`, "
                        f"but expected to have `{', '.join(sorted(expected_item))}` items"
                    )
                    return {"__eq__": msg}

            try:
                self.assertEqual(expected_item, received_item)
                return {}
            except AssertionError:
                msg = f"Received `{received_item}`, but expected `{expected_item}`"
                if not isinstance(received_item, type(expected_item)):
                    msg = (
                        f"Received `{type(received_item)} - {received_item}`, "
                        f"but expected `{type(expected_item)} - {expected_item}`"
                    )

                return {"__eq__": msg}

        errors = _compare(expected_item=expected, received_item=received)
        if errors:
            msg = f"There's {len(errors)} fields that differ"
            differ_report = "\n".join([f"- {key}: {msg} " for key, msg in errors.items()])
            msg += f"\n{differ_report}"
            raise AssertionError(msg)

    def patch_env(self, include_existing=False, **kwargs):
        all_envs = kwargs.copy()
        if include_existing:
            all_envs.update(os.environ)
        return patch.dict(os.environ, all_envs)

    def patch_time(self, some_date):
        return patch("django.utils.timezone.now", return_value=some_date)

    def patch_cache_lock(
        self,
        lock_side_effect: Optional[Union[Callable, Exception, Type[Exception]]] = None,
        unlock_side_effect: Optional[Union[Callable, Exception, Type[Exception]]] = None,
    ):
        class CacheAssertion:
            def __init__(self):
                self.call_count = 0
                self.call_args = []
                self.call_kwargs = {}

            def start(self):
                setattr(ConnectionProxy, "lock", mocked_lock)

            def stop(self):
                delattr(ConnectionProxy, "lock")

            def __enter__(self):
                self.start()
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                self.stop()

            def assert_called(self):
                msg = "Expected to be called, but it was not"
                assert self.call_count > 0, msg

            def assert_called_with(self, *expected_args, **expected_kwargs):
                self.assert_called()

                lock_args = self.call_args  # remove the self argument
                msg = (
                    f"Expected to lock with {len(expected_args)} args: {', '.join(expected_args)}. "
                    f"But locked with {len(lock_args)} args: {', '.join(lock_args)}"
                )
                assert len(expected_args) == len(lock_args), msg

                for expected, received in zip(expected_args, lock_args):
                    msg = f"Expected to lock with {expected}, but locked with {received}"
                    assert expected == received, msg

                lock_kwargs = self.call_kwargs
                msg = (
                    f"Expected to lock with {len(expected_kwargs)} kwargs: {', '.join(expected_kwargs)}. "
                    f"But locked with {len(lock_kwargs)} kwargs: {', '.join(lock_kwargs)}"
                )
                assert len(expected_kwargs) == len(lock_kwargs), msg

                for expected_key, expected_value in expected_kwargs.items():
                    received = lock_kwargs.get(expected_key)
                    msg = f"Expected to lock with {expected_key}={expected_value}, but locked with {received}"
                    assert expected_value == received, msg

        assertion = CacheAssertion()

        def _execute_effect(effect):
            if effect:
                if inspect.isclass(effect) and issubclass(effect, Exception):
                    raise effect()
                if isinstance(effect, Exception):
                    raise effect
                if callable(effect):
                    effect()

        @contextmanager
        def mocked_lock(*lock_args, **lock_kwargs):
            nonlocal assertion

            assertion.call_count += 1
            assertion.call_args = lock_args[1:]  # remove self argument
            assertion.call_kwargs = lock_kwargs

            _execute_effect(effect=lock_side_effect)
            yield
            _execute_effect(effect=unlock_side_effect)

        return assertion
