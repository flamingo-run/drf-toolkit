import zoneinfo
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from django.db.backends.postgresql.psycopg_any import Range

from drf_kit.serializers import as_dict, as_str
from drf_kit.tests import BaseApiTest


class TestAsDict(BaseApiTest):
    def test_zoneinfo_object_as_dict(self):
        timezone_key = "America/Sao_Paulo"
        zoneinfo_timezone = as_dict(ZoneInfo(key=timezone_key))
        self.assertEqual(timezone_key, zoneinfo_timezone)
        self.assertIsInstance(zoneinfo_timezone, str)

    def test_timezone_object_as_dict(self):
        timezone_key = "America/Sao_Paulo"
        timezone = as_dict(zoneinfo.ZoneInfo(timezone_key))
        self.assertEqual(timezone_key, timezone)
        self.assertIsInstance(timezone, str)

    def test_range_as_dict(self):
        lower = datetime(2023, 9, 27, 15, 0, 0, tzinfo=UTC)
        upper = lower + timedelta(days=5)
        range = Range(lower=lower, upper=upper)
        self.assertEqual(as_dict(range), [as_str(lower), as_str(upper)])

        lower = datetime(2023, 9, 27, 15, 0, 0, tzinfo=UTC)
        range = Range(lower=lower)
        self.assertEqual(as_dict(range), [as_str(lower), None])

        upper = datetime(2023, 9, 27, 15, 0, 0, tzinfo=UTC)
        range = Range(upper=upper)
        self.assertEqual(as_dict(range), [None, as_str(upper)])
