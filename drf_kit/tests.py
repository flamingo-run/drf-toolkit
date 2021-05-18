import os
import re
from io import StringIO
from unittest.mock import patch, ANY

from django.core.cache import cache
from django.core.management import call_command
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

    def assertUUIDFilePath(self, prefix, name, extension, pk, file):  # pylint: disable=invalid-name
        expected_path = r"^{prefix}/{pk}/{name}_{uuid}\.{extension}$".format(
            prefix=prefix,
            pk=pk,
            name=name,
            extension=extension,
            uuid=r"[0-9a-f]{8}\-[0-9a-f]{4}\-4[0-9a-f]{3}\-[89ab][0-9a-f]{3}\-[0-9a-f]{12}",
        )
        self.assertTrue(re.match(expected_path, str(file)))

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

            if isinstance(expected_item, list) and isinstance(received_item, list):
                if len(expected_item) != len(received_item):
                    msg = f"Received {len(received_item)} items and it was expected to have {len(expected_item)}"
                    return {"__len__": msg}

                for _idx, (_expected_item, _received_item) in enumerate(zip(expected_item, received_item)):
                    return _assert_dict(idx=_idx, expected_item=_expected_item, received_item=_received_item)
            elif isinstance(expected_item, dict) and isinstance(received_item, dict):
                return _assert_dict(expected_item=expected_item, received_item=received_item)
            else:
                try:
                    self.assertEqual(expected_item, received_item)
                    return {}
                except AssertionError:
                    msg = f"Received `{received_item}`, but expected `{expected_item}`"
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
