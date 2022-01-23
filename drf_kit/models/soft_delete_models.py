import logging

from django.db import models
from django.db.models.signals import pre_save
from django.utils.timezone import now
from django.utils.translation import gettext as _

from drf_kit import exceptions, managers, signals
from drf_kit.models.base_models import BaseModel

logger = logging.getLogger(__name__)


def verify_soft_deletion(sender, instance, **kwargs):
    if instance.is_deleted and not instance._state.adding:
        raise exceptions.UpdatingSoftDeletedException()


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

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        pre_save.connect(verify_soft_deletion, cls)

    objects = managers.SoftDeleteManager()

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    def delete(self, using=None, keep_parents=False):
        if not self.is_deleted:
            signals.pre_soft_delete.send(
                sender=self.__class__,
                instance=self,
            )

            # save & skip signals
            self.deleted_at = now()
            from drf_kit.signals import UnplugSignal  # pylint: disable=import-outside-toplevel

            with UnplugSignal(signal=pre_save, func=verify_soft_deletion, model=self.__class__):
                self.save()

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
