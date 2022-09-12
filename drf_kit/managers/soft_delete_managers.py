from django.db import models
from django.db.models import Q, query
from ordered_model.models import OrderedModelQuerySet

from drf_kit.managers.availability_managers import AvailabilityManager


class SoftDeleteFilters:
    @classmethod
    def deleted(cls):
        return Q(deleted_at__isnull=False)


class SoftDeleteQuerySet(query.QuerySet):
    def all_with_deleted(self):
        qs = super().all()
        qs.__class__ = SoftDeleteQuerySet
        return qs

    def delete(self):
        if not bool(self):
            return False, 0
        deleted = 0
        for obj in self:
            obj.delete()
            deleted += 1
        return True, deleted

    def hard_delete(self):
        return super().delete()

    def undelete(self):
        return self.update(deleted_at=None)


class SoftDeleteManager(models.Manager):
    queryset_class = SoftDeleteQuerySet

    def get_queryset(self):
        qs = super().get_queryset().exclude(SoftDeleteFilters.deleted())
        if not issubclass(qs.__class__, SoftDeleteQuerySet):
            qs.__class__ = self.queryset_class
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

        if not issubclass(qs.__class__, SoftDeleteQuerySet):
            qs.__class__ = SoftDeleteQuerySet
        return qs


class SoftDeleteOrderedQueryset(SoftDeleteQuerySet, OrderedModelQuerySet):
    def all_with_deleted(self):
        qs = super().all()
        qs.__class__ = SoftDeleteOrderedQueryset
        return qs


class SoftDeleteOrderedManager(SoftDeleteManager):
    queryset_class = SoftDeleteOrderedQueryset


class SoftDeleteAvailabilityManager(AvailabilityManager, SoftDeleteManager):
    ...
