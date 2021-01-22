import os
import re
from io import StringIO
from unittest.mock import patch

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

    def patch_env(self, include_existing=False, **kwargs):
        all_envs = kwargs.copy()
        if include_existing:
            all_envs.update(os.environ)
        return patch.dict(os.environ, all_envs)

    def patch_time(self, some_date):
        return patch('django.utils.timezone.now', return_value=some_date)
