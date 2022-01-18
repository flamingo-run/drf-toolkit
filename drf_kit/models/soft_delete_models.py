import logging

from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext as _

from drf_kit import exceptions, managers, signals
from drf_kit.models.base_models import BaseModel

logger = logging.getLogger(__name__)


class SoftDeleteModelMixin(models.Model):
    deleted_at = models.DateTimeField(
        verbose_name=_("deleted at"),
        blank=True,
        null=True,
        default=None,
    )

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=["deleted_at"]),
        ]

    objects = managers.SoftDeleteManager()

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    def save(self, *args, soft_deleting=False, **kwargs):  # pylint: disable=arguments-differ
        if self.is_deleted and not soft_deleting and not self._state.adding:
            raise exceptions.UpdatingSoftDeletedException()
        return super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        if not self.is_deleted:
            signals.pre_soft_delete.send(
                sender=self.__class__,
                instance=self,
            )

            self.deleted_at = now()
            self.save(soft_deleting=True)

            signals.post_soft_delete.send(
                sender=self.__class__,
                instance=self,
            )

    def undelete(self):
        if self.is_deleted:
            signals.pre_undelete.send(
                sender=self.__class__,
                instance=self,
            )

            self.deleted_at = None
            self.save()

            signals.post_undelete.send(
                sender=self.__class__,
                instance=self,
            )


class SoftDeleteModel(SoftDeleteModelMixin, BaseModel):
    class Meta(SoftDeleteModelMixin.Meta, BaseModel.Meta):
        abstract = True
        indexes = BaseModel.Meta.indexes + SoftDeleteModelMixin.Meta.indexes
