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
        return self.settings(
            CACHES={
                'default': {
                    'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
                }
            }
        )

    def assertNoPendingMigration(self, app_name):
        out = StringIO()
        message = None
        try:
            call_command(
                'makemigrations',
                app_name,
                '--check',
                '--dry-run',
                interactive=False,
                stdout=out
            )
        except SystemExit:
            message = f'Missing migration. Run python manage.py makemigrations {app_name}'
        self.assertIn('No changes', out.getvalue(), msg=message)

    def assertUUIDFilePath(self, prefix, name, extension, pk, file):
        expected_path = r'^{prefix}/{pk}/{name}_{uuid}\.{extension}$'.format(
            prefix=prefix,
            pk=pk,
            name=name,
            extension=extension,
            uuid=r'[0-9a-f]{8}\-[0-9a-f]{4}\-4[0-9a-f]{3}\-[89ab][0-9a-f]{3}\-[0-9a-f]{12}',
        )
        self.assertTrue(re.match(expected_path, str(file)))

    def assertResponseMatch(self, expected, received):
        def _assert_dict(expected_item, received_item, idx=None):
            msg = f"At item #{idx}:: " if idx else ""
            if expected_item == received_item:
                return

            expected_keys = set(expected_item)
            received_keys = set(received_item)
            if expected_keys != received_keys:
                missing_keys = expected_keys - received_keys
                if missing_keys:
                    msg += f"There's {len(missing_keys)} fields missing: {' | '.join(missing_keys)}"
                    raise AssertionError(msg)

                extra_keys = received_keys - expected_keys
                if extra_keys:
                    msg += f"There's {len(extra_keys)} unexpected fields: {' | '.join(extra_keys)}"
                    raise AssertionError(msg)

            diff_keys = set()
            for key in expected_item:
                if expected_item[key] == ANY:
                    continue

                if expected_item[key] != received_item[key]:
                    diff_keys.add(key)

            if not diff_keys:
                return

            msg += f"There's {len(diff_keys)} fields that differ"
            differ_report = '\n'.join([
                f'- {key}: Received {received_item[key]}, but expected {expected_item[key]} '
                for key in diff_keys
            ])
            msg += f"\n{differ_report}"
            raise AssertionError(msg)

        if isinstance(expected, list) and isinstance(received, list):
            if len(expected) != len(received):
                msg = f"Received {len(received)} items and it was expected to have {len(expected)}"
                raise AssertionError(msg)

            for _idx, (_expected_item, _received_item) in enumerate(zip(expected, received)):
                _assert_dict(idx=_idx, expected_item=_expected_item, received_item=_received_item)
        elif isinstance(expected, dict) and isinstance(received, dict):
            _assert_dict(expected_item=expected, received_item=received)
        else:
            super().assertEqual(expected, received)

    def patch_env(self, include_existing=False, **kwargs):
        all_envs = kwargs.copy()
        if include_existing:
            all_envs.update(os.environ)
        return patch.dict(os.environ, all_envs)

    def patch_time(self, some_date):
        return patch('django.utils.timezone.now', return_value=some_date)
