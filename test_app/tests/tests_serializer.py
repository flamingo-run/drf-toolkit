from zoneinfo import ZoneInfo
import pytz

from drf_kit.tests import BaseApiTest
from drf_kit.serializers import as_dict


class TestAsDict(BaseApiTest):
    def test_zoneinfo_object_as_dict(self):
        timezone_key = "America/Sao_Paulo"
        zoneinfo_timezone = as_dict(ZoneInfo(key=timezone_key))
        self.assertEqual(timezone_key, zoneinfo_timezone)
        self.assertIsInstance(zoneinfo_timezone, str)

    def test_pytz_timezone_object_as_dict(self):
        timezone_key = "America/Sao_Paulo"
        pytz_timezone = as_dict(pytz.timezone(timezone_key))
        self.assertEqual(timezone_key, pytz_timezone)
        self.assertIsInstance(pytz_timezone, str)
