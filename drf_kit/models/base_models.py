import logging

from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _

from drf_kit.models.diff_models import ModelDiffMixin
from drf_kit.models.file_models import BoundedFileMixin

logger = logging.getLogger(__name__)


class BaseModel(ModelDiffMixin, BoundedFileMixin, models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("created at"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("updated at"),
    )

    objects = models.Manager()

    class Meta:
        abstract = True
        ordering = ("-updated_at",)
        get_latest_by = "updated_at"
        indexes = [
            models.Index(fields=["updated_at"]),
        ]

    def admin_edit_url(self):
        return reverse(
            f"admin:{self._meta.app_label}_{self._meta.model_name}_change",  # pylint: disable=no-member
            args=[self.pk],
        )

    def __repr__(self):
        return f"<{self._meta.app_label}.{self.__class__.__name__} {self.pk}>"  # pylint: disable=no-member
