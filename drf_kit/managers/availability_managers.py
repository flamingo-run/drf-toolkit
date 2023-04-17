from dataclasses import dataclass
from datetime import datetime

from django.db import models
from django.db.models import Q
from django.utils import timezone


@dataclass
class AvailabilityChecker:
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    at: datetime | None = None

    def __post_init__(self):
        self.at = self.at or timezone.now()

    @property
    def is_future(self) -> bool:
        not_started = self.future_start
        not_ended = self.future_end or self.undefined_end
        return not_started and not_ended

    @property
    def is_past(self) -> bool:
        started = self.past_start or self.undefined_start
        ended = self.past_end
        return started and ended

    @property
    def is_current(self) -> bool:
        started = self.past_start or self.undefined_start
        not_ended = self.future_end or self.undefined_end
        return started & not_ended

    @property
    def undefined_start(self) -> bool:
        return self.starts_at is None

    @property
    def undefined_end(self) -> bool:
        return self.ends_at is None

    @property
    def past_start(self) -> bool:
        return not self.undefined_start and self.starts_at <= self.at  # now is considered in the past

    @property
    def past_end(self) -> bool:
        return not self.undefined_end and self.ends_at <= self.at  # now is considered in the past

    @property
    def future_start(self) -> bool:
        return not self.undefined_start and self.starts_at > self.at

    @property
    def future_end(self) -> bool:
        return not self.undefined_end and self.ends_at > self.at


class AvailabilityFilters:
    @classmethod
    def future(cls, dt: datetime | None = None):
        not_started = cls.future_start(dt=dt)
        not_ended = cls.future_end(dt=dt) | cls.undefined_end()
        return not_started & not_ended

    @classmethod
    def past(cls, dt: datetime | None = None):
        started = cls.past_start(dt=dt) | cls.undefined_start()
        ended = cls.past_end(dt=dt)
        return started & ended

    @classmethod
    def current(cls, dt: datetime | None = None):
        started = cls.past_start(dt=dt) | cls.undefined_start()
        not_ended = cls.future_end(dt=dt) | cls.undefined_end()
        return started & not_ended

    @classmethod
    def same_availability(cls, starts_at: datetime | None = None, ends_at: datetime | None = None):
        if not starts_at and not ends_at:
            # When it does have either start and end,
            # any other similar patient_care_team will match
            return Q()

        # Any other similar patient_care_team that has
        # both open start and open end will match
        filters = cls.undefined_start() & cls.undefined_end()

        if ends_at:
            # When it has an end,
            # any other similar patient_care_team with a range that overlaps will match
            filters |= Q(starts_at__isnull=True, ends_at__gte=ends_at)
            filters |= Q(starts_at__lt=ends_at, ends_at__gte=ends_at)

            # or any other similar that is within the range will match
            filters |= Q(starts_at__isnull=True, ends_at__lte=ends_at)
            if starts_at:
                filters |= Q(starts_at__gte=starts_at, ends_at__lte=ends_at)

        if starts_at:
            # When it has a start,
            # any other similar patient_care_team with a range that overlaps will match
            filters |= Q(starts_at__lte=starts_at, ends_at__isnull=True)
            filters |= Q(starts_at__lte=starts_at, ends_at__gt=starts_at)

            # or any other similar that is within the range will match
            filters |= Q(starts_at__gte=starts_at, ends_at__isnull=True)
            if ends_at:
                filters |= Q(starts_at__gte=starts_at, ends_at__lte=ends_at)

        return filters

    @classmethod
    def undefined_start(cls):
        return Q(starts_at__isnull=True)

    @classmethod
    def undefined_end(cls):
        return Q(ends_at__isnull=True)

    @classmethod
    def past_start(cls, dt: datetime | None = None):
        dt = dt or timezone.now()
        return Q(starts_at__lte=dt)  # now is considered in the past

    @classmethod
    def past_end(cls, dt: datetime | None = None):
        dt = dt or timezone.now()
        return Q(ends_at__lte=dt)  # now is considered in the past

    @classmethod
    def future_start(cls, dt: datetime | None = None):
        dt = dt or timezone.now()
        return Q(starts_at__gt=dt)

    @classmethod
    def future_end(cls, dt: datetime | None = None):
        dt = dt or timezone.now()
        return Q(ends_at__gt=dt)


class AvailabilityManager(models.Manager):
    def current(self, at: datetime | None = None):
        return super().get_queryset().filter(AvailabilityFilters.current(dt=at))

    def past(self, at: datetime | None = None):
        return super().get_queryset().filter(AvailabilityFilters.past(dt=at))

    def future(self, at: datetime | None = None):
        return super().get_queryset().filter(AvailabilityFilters.future(dt=at))

    def same_availability_of(self, obj: "drf_kit.models.AvailabilityModel"):  # noqa: F821
        if not hasattr(obj, "starts_at") or not hasattr(obj, "ends_at"):
            raise TypeError(f"Expected AvailabilityModel, got {type(obj)}")

        same_range_filter = AvailabilityFilters.same_availability(starts_at=obj.starts_at, ends_at=obj.ends_at)
        return super().get_queryset().filter(same_range_filter).exclude(id=obj.pk)
