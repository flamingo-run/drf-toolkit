from datetime import timedelta

from django.db import IntegrityError
from django.utils import timezone

from drf_kit.tests import BaseApiTest
from test_app.models import RoomOfRequirement
from test_app.tests.factories.room_of_requirement_factories import RoomOfRequirementFactory
from test_app.tests.tests_base import HogwartsTestMixin


class TestAvailabilityModel(HogwartsTestMixin, BaseApiTest):
    def setUp(self):
        super().setUp()

        # An extensive data setup that will be used across all tests in this class
        self.reference_date = timezone.now()
        self.very_past_date = self.reference_date - timedelta(days=10)
        self.past_date = self.reference_date - timedelta(days=1)
        self.future_date = self.reference_date + timedelta(days=1)
        self.very_future_date = self.reference_date + timedelta(days=10)

        self.past = [
            RoomOfRequirementFactory(starts_at=self.very_past_date, ends_at=self.past_date),
            RoomOfRequirementFactory(starts_at=None, ends_at=self.past_date),
            RoomOfRequirementFactory(starts_at=None, ends_at=self.very_past_date),
        ]
        self.current = [
            RoomOfRequirementFactory(starts_at=self.past_date, ends_at=self.future_date),
            RoomOfRequirementFactory(starts_at=None, ends_at=self.future_date),
            RoomOfRequirementFactory(starts_at=None, ends_at=self.future_date),
            RoomOfRequirementFactory(starts_at=self.past_date, ends_at=None),
            RoomOfRequirementFactory(starts_at=self.very_past_date, ends_at=None),
            RoomOfRequirementFactory(starts_at=None, ends_at=None),
        ]
        self.future = [
            RoomOfRequirementFactory(starts_at=self.future_date, ends_at=self.very_future_date),
            RoomOfRequirementFactory(starts_at=self.future_date, ends_at=None),
            RoomOfRequirementFactory(starts_at=self.very_future_date, ends_at=None),
        ]

    def assertObjects(self, qs, expected):  # pylint: disable=invalid-name
        self.assertEqual(len(expected), qs.count())
        for obj in qs:
            self.assertIn(obj, expected)

    def assertInconsistent(self):  # pylint: disable=invalid-name
        return self.assertRaisesRegex(expected_exception=IntegrityError, expected_regex=r"invalid_date_range")

    def test_query_default(self):
        qs = RoomOfRequirement.objects.all()

        expected = self.past + self.current + self.future
        self.assertObjects(qs=qs, expected=expected)

    def test_query_past(self):
        qs = RoomOfRequirement.objects.past()

        expected = self.past
        self.assertObjects(qs=qs, expected=expected)

    def test_query_current(self):
        qs = RoomOfRequirement.objects.current()

        expected = self.current
        self.assertObjects(qs=qs, expected=expected)

    def test_query_future(self):
        qs = RoomOfRequirement.objects.future()

        expected = self.future
        self.assertObjects(qs=qs, expected=expected)

    def test_past_objects(self):
        for obj in self.past:
            self.assertTrue(obj.is_past)
            self.assertFalse(obj.is_current)
            self.assertFalse(obj.is_future)

    def test_current_objects(self):
        for obj in self.current:
            self.assertFalse(obj.is_past)
            self.assertTrue(obj.is_current)
            self.assertFalse(obj.is_future)

    def test_future_objects(self):
        for obj in self.future:
            self.assertFalse(obj.is_past)
            self.assertFalse(obj.is_current)
            self.assertTrue(obj.is_future)

    def test_range_inconsistency(self):
        inconsistencies = [
            (self.future_date, self.past_date),
            (self.future_date, self.very_past_date),
            (self.very_future_date, self.past_date),
            (self.very_future_date, self.very_past_date),
        ]

        for starts_at, ends_at in inconsistencies:
            with self.assertInconsistent():
                RoomOfRequirementFactory(starts_at=starts_at, ends_at=ends_at)
