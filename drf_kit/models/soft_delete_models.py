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

    objects = managers.SoftDeleteManager()

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=["deleted_at"]),
        ]

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        pre_save.connect(verify_soft_deletion, cls)

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    def delete(self, using=None, keep_parents=False):
        if not self.is_deleted:
            signals.pre_soft_delete.send(sender=self.__class__, instance=self)

            # save & skip signals
            self.deleted_at = now()
            from drf_kit.signals import UnplugSignal  # pylint: disable=import-outside-toplevel

            with UnplugSignal(signal=pre_save, func=verify_soft_deletion, model=self.__class__):
                self.save(update_fields=self._changed_fields)

            signals.post_soft_delete.send(sender=self.__class__, instance=self)

            # Delete related
            all_related = [
                f
                for f in self._meta.get_fields()
                if (f.one_to_many or f.one_to_one) and f.auto_created and not f.concrete
            ]

            for related in all_related:
                on_delete = related.on_delete.__name__
                if on_delete not in ("CASCADE", "SET_NULL"):
                    continue

                relation_field = related.get_accessor_name()
                try:
                    value = getattr(self, relation_field)
                except related.related_model.DoesNotExist:
                    continue

                match related.one_to_one, on_delete,:
                    case True, "CASCADE":
                        value.delete()
                    case True, "SET_NULL":
                        setattr(value, related.field.name, None)
                        value.save()
                    case False, "CASCADE":
                        value.all().delete()
                    case False, "SET_NULL":
                        value.update(**{related.field.name: None})
        else:
            super().delete(using=using, keep_parents=keep_parents)

    def undelete(self):
        if self.is_deleted:
            signals.pre_undelete.send(
                sender=self.__class__,
                instance=self,
            )

            self.deleted_at = None
            self.save(update_fields=self._changed_fields)

            signals.post_undelete.send(
                sender=self.__class__,
                instance=self,
            )


class SoftDeleteModel(SoftDeleteModelMixin, BaseModel):
    class Meta(SoftDeleteModelMixin.Meta, BaseModel.Meta):
        abstract = True
        indexes = BaseModel.Meta.indexes + SoftDeleteModelMixin.Meta.indexes
