import logging

from django.db import models
from django.utils.translation import gettext as _

from drf_kit import managers
from drf_kit.models.base_models import BaseModel

logger = logging.getLogger(__name__)


class AvailabilityModelMixin(models.Model):
    starts_at = models.DateTimeField(
        verbose_name=_("starts at"),
        blank=True,
        null=True,
        default=None,
    )
    ends_at = models.DateTimeField(
        verbose_name=_("ends at"),
        blank=True,
        null=True,
        default=None,
    )

    objects = managers.AvailabilityManager()

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=["starts_at"]),
            models.Index(fields=["ends_at"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(starts_at__lte=models.F("ends_at")),
                name="%(class)s_invalid_date_range",
            ),
        ]

    @property
    def is_future(self) -> bool:
        return self._availability_checker.is_future

    @property
    def is_past(self) -> bool:
        return self._availability_checker.is_past

    @property
    def is_current(self) -> bool:
        return self._availability_checker.is_current

    @property
    def _availability_checker(self) -> managers.AvailabilityChecker:
        return managers.AvailabilityChecker(starts_at=self.starts_at, ends_at=self.ends_at)


class AvailabilityModel(AvailabilityModelMixin, BaseModel):
    class Meta(AvailabilityModelMixin.Meta, BaseModel.Meta):
        abstract = True
        indexes = BaseModel.Meta.indexes + AvailabilityModelMixin.Meta.indexes
