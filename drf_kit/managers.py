from django.db import models
from django.db.models import query
from django.utils import timezone


class SoftDeleteQuerySet(query.QuerySet):
    def all_with_deleted(self):
        qs = super().all()
        qs.__class__ = SoftDeleteQuerySet
        return qs

    def delete(self):
        if not bool(self):
            return
        self.update(deleted_at=timezone.now())

    def undelete(self, *args, using="default", **kwargs):
        self.update(deleted_at=None)


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .filter(
                deleted_at__isnull=True,
            )
        )
        qs.__class__ = SoftDeleteQuerySet
        return qs

    def all_with_deleted(self, prt=False):
        qs = super().get_queryset()
        return qs

    def get(self, *args, **kwargs):
        return self._get_base_queryset(*args, **kwargs).get(*args, **kwargs)

    def filter(self, *args, **kwargs):
        return self._get_base_queryset(*args, **kwargs).filter(*args, **kwargs)

    def _get_base_queryset(self, *args, **kwargs):
        if "pk" in kwargs:
            qs = self.all_with_deleted()
        else:
            qs = self.all()
        return qs
