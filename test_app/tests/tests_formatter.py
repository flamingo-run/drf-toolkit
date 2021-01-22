from datetime import datetime, timezone

import pytz

from drf_kit import serializers
from drf_kit.tests import BaseApiTest


class TestFormatAsStr(BaseApiTest):
    def non_utc(self, dt):
        return pytz.timezone("Hongkong").localize(dt)

    def test_format_none(self):
        as_str = serializers.as_str(None)
        self.assertEqual(None, as_str)

    def test_format_boolean(self):
        as_str = serializers.as_str(True)
        self.assertEqual('True', as_str)

    def test_format_naive_datetime(self):
        naive = datetime(1990, 7, 19, 15, 43, 20)
        as_str = serializers.as_str(naive)
        self.assertEqual('1990-07-19T15:43:20Z', as_str)

    def test_format_naive_milliseconds_datetime(self):
        naive = datetime(1990, 7, 19, 15, 43, 20, 999999)
        as_str = serializers.as_str(naive)
        self.assertEqual('1990-07-19T15:43:20Z', as_str)

    def test_format_utc_timezoned_datetime(self):
        timezoned = datetime(1990, 7, 19, 15, 43, 20, tzinfo=timezone.utc)
        as_str = serializers.as_str(timezoned)
        self.assertEqual('1990-07-19T15:43:20Z', as_str)

    def test_format_non_utc_timezoned_datetime(self):
        timezoned = self.non_utc(datetime(1990, 7, 19, 15, 43, 20))
        as_str = serializers.as_str(timezoned)
        self.assertEqual('1990-07-19T07:43:20Z', as_str)

    def test_format_utc_timezoned_milliseconds_datetime(self):
        timezoned = datetime(1990, 7, 19, 15, 43, 20, 999999, tzinfo=timezone.utc)
        as_str = serializers.as_str(timezoned)
        self.assertEqual('1990-07-19T15:43:20Z', as_str)


class TestAssureTimezone(BaseApiTest):
    def non_utc(self, dt):
        return pytz.timezone("Hongkong").localize(dt)

    def test_empty_date(self):
        as_str = serializers.assure_tz(None)
        self.assertEqual(None, as_str)

    def test_timezoned_datetime(self):
        timezoned = datetime(1990, 7, 19, 15, 43, 20, tzinfo=timezone.utc)
        assured_dt = serializers.assure_tz(timezoned)
        self.assertEqual(timezoned, assured_dt)

    def test_naive_datetime(self):
        timezoned = datetime(1990, 7, 19, 15, 43, 20)
        assured_dt = serializers.assure_tz(timezoned)
        self.assertEqual(timezoned.replace(tzinfo=timezone.utc), assured_dt)

    def test_naive_datetime_custom_timezone(self):
        timezoned = datetime(1990, 7, 19, 15, 43, 20)
        assured_dt = serializers.assure_tz(timezoned, tz=pytz.timezone("Hongkong"))
        self.assertEqual(self.non_utc(timezoned), assured_dt)
