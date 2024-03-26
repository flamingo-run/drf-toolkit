from datetime import timedelta

from dateutil.parser import parse
from django.db import IntegrityError
from django.utils import timezone
from freezegun import freeze_time

from drf_kit.tests import BaseApiTest
from test_app.models import RoomOfRequirement
from test_app.tests.factories.room_of_requirement_factories import RoomOfRequirementFactory
from test_app.tests.factories.wizard_factories import WizardFactory
from test_app.tests.tests_base import HogwartsTestMixin


class TestAvailabilityModel(HogwartsTestMixin, BaseApiTest):
    factory_class = RoomOfRequirementFactory

    @property
    def model_class(self):
        return self.factory_class._meta.model

    def setUp(self):
        super().setUp()

        # An extensive data setup that will be used across all tests in this class
        self.reference_date = timezone.now()
        self.very_past_date = self.reference_date - timedelta(days=10)
        self.past_date = self.reference_date - timedelta(days=1)
        self.future_date = self.reference_date + timedelta(days=1)
        self.very_future_date = self.reference_date + timedelta(days=10)

        self.past = [
            self.factory_class(starts_at=self.very_past_date, ends_at=self.past_date),
            self.factory_class(starts_at=None, ends_at=self.past_date),
            self.factory_class(starts_at=None, ends_at=self.very_past_date),
        ]
        self.current = [
            self.factory_class(starts_at=self.past_date, ends_at=self.future_date),
            self.factory_class(starts_at=None, ends_at=self.future_date),
            self.factory_class(starts_at=None, ends_at=self.future_date),
            self.factory_class(starts_at=self.past_date, ends_at=None),
            self.factory_class(starts_at=self.very_past_date, ends_at=None),
            self.factory_class(starts_at=None, ends_at=None),
        ]
        self.future = [
            self.factory_class(starts_at=self.future_date, ends_at=self.very_future_date),
            self.factory_class(starts_at=self.future_date, ends_at=None),
            self.factory_class(starts_at=self.very_future_date, ends_at=None),
        ]

    def assertObjects(self, qs, expected):
        self.assertEqual(len(expected), qs.count())
        for obj in qs:
            self.assertIn(obj, expected)

    def assertInconsistent(self):
        return self.assertRaisesRegex(expected_exception=IntegrityError, expected_regex=r"_invalid_date_range")

    def test_query_default(self):
        qs = self.model_class.objects.all()

        expected = self.past + self.current + self.future
        self.assertObjects(qs=qs, expected=expected)

    def test_query_past(self):
        qs = self.model_class.objects.past()

        expected = self.past
        self.assertObjects(qs=qs, expected=expected)

    def test_query_current(self):
        qs = self.model_class.objects.current()

        expected = self.current
        self.assertObjects(qs=qs, expected=expected)

    def test_query_future(self):
        qs = self.model_class.objects.future()

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
                self.factory_class(starts_at=starts_at, ends_at=ends_at)


@freeze_time("1990-07-19T12:30:45Z")
class TestAvailabilityModelFrozenInTime(TestAvailabilityModel):
    def setUp(self):
        super().setUp()

        self.now = timezone.now()

        self.past.extend(
            [
                self.factory_class(starts_at=self.past_date, ends_at=self.now),
                self.factory_class(starts_at=None, ends_at=self.now),
            ],
        )

        self.current.extend(
            [
                self.factory_class(starts_at=self.now, ends_at=self.future_date),
                self.factory_class(starts_at=self.now, ends_at=None),
            ],
        )


class TestAvailabilityModelSimilar(HogwartsTestMixin, BaseApiTest):
    def test_closed_range(self):
        config = dict(
            wizard=WizardFactory(),
        )

        past_3, past_2, past_1, future_1, future_2, future_3 = (
            parse("2000-12-15T00:00:00Z") + timedelta(days=i) for i in (-15, -10, -5, 5, 10, 15)
        )

        RoomOfRequirementFactory.create(starts_at=past_1, ends_at=future_1, **config)  # current
        RoomOfRequirementFactory.create(starts_at=past_2, ends_at=past_1, **config)  # past
        RoomOfRequirementFactory.create(starts_at=future_1, ends_at=future_2, **config)  # future

        failures = [
            RoomOfRequirementFactory.build(starts_at=past_1, ends_at=future_2, **config),  # current
            RoomOfRequirementFactory.build(starts_at=past_2, ends_at=past_1, **config),  # past
            RoomOfRequirementFactory.build(starts_at=future_1, ends_at=future_2, **config),  # future
            RoomOfRequirementFactory.build(starts_at=None, ends_at=future_2, **config),  # current
            RoomOfRequirementFactory.build(starts_at=past_1, ends_at=None, **config),  # current
            RoomOfRequirementFactory.build(starts_at=past_3, ends_at=past_1, **config),  # past-conflict
            RoomOfRequirementFactory.build(starts_at=future_1, ends_at=future_3, **config),  # future-conflict
            RoomOfRequirementFactory.build(starts_at=past_3, ends_at=future_3, **config),  # all-conflict
            RoomOfRequirementFactory.build(starts_at=None, ends_at=None, **config),  # all-conflict
        ]

        for failure in failures:
            same_availability = RoomOfRequirement.objects.same_availability_of(obj=failure)
            msg = f"Failed to detect conflict when {failure.starts_at} - {failure.ends_at}"
            self.assertTrue(same_availability.exists(), msg=msg)

    def test_open_range(self):
        config = dict(
            wizard=WizardFactory(),
        )

        past_3, past_2, past_1, future_1, future_2, future_3 = (
            parse("2000-12-15T00:00:00Z") + timedelta(days=i) for i in (-15, -10, -5, 5, 10, 15)
        )

        RoomOfRequirementFactory.create(starts_at=None, ends_at=None, **config)  # current

        failures = [
            RoomOfRequirementFactory.build(starts_at=past_2, ends_at=past_1, **config),  # past
            RoomOfRequirementFactory.build(starts_at=future_1, ends_at=future_2, **config),  # future
            RoomOfRequirementFactory.build(starts_at=past_1, ends_at=future_2, **config),  # current
            RoomOfRequirementFactory.build(starts_at=past_2, ends_at=past_1, **config),  # past
            RoomOfRequirementFactory.build(starts_at=future_1, ends_at=future_2, **config),  # future
            RoomOfRequirementFactory.build(starts_at=None, ends_at=future_2, **config),  # current
            RoomOfRequirementFactory.build(starts_at=past_1, ends_at=None, **config),  # current
            RoomOfRequirementFactory.build(starts_at=past_3, ends_at=past_1, **config),  # past-conflict
            RoomOfRequirementFactory.build(starts_at=future_1, ends_at=future_3, **config),  # future-conflict
            RoomOfRequirementFactory.build(starts_at=past_3, ends_at=future_3, **config),  # all-conflict
            RoomOfRequirementFactory.build(starts_at=None, ends_at=None, **config),  # all-conflict
        ]

        for failure in failures:
            same_availability = RoomOfRequirement.objects.same_availability_of(obj=failure)
            msg = f"Failed to detect conflict when {failure.starts_at} - {failure.ends_at}"
            self.assertTrue(same_availability.exists(), msg=msg)

    def test_partially_open_range(self):
        config = dict(
            wizard=WizardFactory(),
        )

        past_3, past_2, past_1, future_1, future_2, future_3 = (
            parse("2000-12-15T00:00:00Z") + timedelta(days=i) for i in (-15, -10, -5, 5, 10, 15)
        )

        RoomOfRequirementFactory.create(starts_at=None, ends_at=past_2, **config)  # past
        RoomOfRequirementFactory.create(starts_at=future_2, ends_at=None, **config)  # future

        failures = [
            RoomOfRequirementFactory.build(starts_at=past_2, ends_at=past_1, **config),  # past
            RoomOfRequirementFactory.build(starts_at=future_1, ends_at=future_2, **config),  # future
            RoomOfRequirementFactory.build(starts_at=past_1, ends_at=future_2, **config),  # current
            RoomOfRequirementFactory.build(starts_at=past_2, ends_at=past_1, **config),  # past
            RoomOfRequirementFactory.build(starts_at=future_1, ends_at=future_2, **config),  # future
            RoomOfRequirementFactory.build(starts_at=None, ends_at=future_2, **config),  # current
            RoomOfRequirementFactory.build(starts_at=past_1, ends_at=None, **config),  # current
            RoomOfRequirementFactory.build(starts_at=past_3, ends_at=past_1, **config),  # past-conflict
            RoomOfRequirementFactory.build(starts_at=future_1, ends_at=future_3, **config),  # future-conflict
            RoomOfRequirementFactory.build(starts_at=past_3, ends_at=future_3, **config),  # all-conflict
            RoomOfRequirementFactory.build(starts_at=None, ends_at=None, **config),  # all-conflict
        ]

        for failure in failures:
            same_availability = RoomOfRequirement.objects.same_availability_of(obj=failure)
            msg = f"Failed to detect conflict when {failure.starts_at} - {failure.ends_at}"
            self.assertTrue(same_availability.exists(), msg=msg)

    def test_not_availability_model(self):
        with self.assertRaisesRegex(TypeError, "Expected AvailabilityModel, got"):
            RoomOfRequirement.objects.same_availability_of(obj=WizardFactory())
