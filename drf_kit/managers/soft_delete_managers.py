from collections.abc import Generator, Iterable

from django.db import models
from django.db.models import ManyToManyRel, ManyToOneRel, Q, query
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

    def filter(self, *args, **kwargs):
        # Unfortunately, Django does not support using manager when filtering M2M relationships
        # https://docs.djangoproject.com/en/dev/topics/db/managers/#base-managers
        # So we must manually detect if a M2M relationship is being filtered
        # and add the extra filter to exclude deleted objects
        for extra_filter in self._get_extra_filters(fields=kwargs.keys()):
            kwargs |= extra_filter
        return super().filter(*args, **kwargs)

    def _get_m2m_relations_for(self, fields: Iterable[str]) -> Generator["SoftDeleteModel", None, None]:  # noqa: F821
        from drf_kit.models import SoftDeleteModel

        related_fields = {field.split("__")[0] for field in fields}

        # Check if any of the fields being used to filter has a M2M relationship with SoftDelete
        def _get_m2m_with_soft_delete(
            field_name: str, m2m_rel: ManyToManyRel | ManyToOneRel,
        ) -> type[SoftDeleteModel] | None:
            if field_name not in related_fields:
                return None
            if isinstance(m2m_rel, ManyToManyRel) and m2m_rel.through and issubclass(m2m_rel.through, SoftDeleteModel):
                return m2m_rel.through
            if isinstance(m2m_rel, ManyToOneRel) and issubclass(m2m_rel.model, SoftDeleteModel):
                return m2m_rel.model
            return None

        for rel_obj in self.model._meta.related_objects:  # Direct M2M relations
            if rel_model := _get_m2m_with_soft_delete(field_name=rel_obj.name, m2m_rel=rel_obj):
                yield rel_model

        for field_obj in self.model._meta.many_to_many:  # Reverse M2M relations
            rel_obj = field_obj.remote_field
            if rel_model := _get_m2m_with_soft_delete(field_name=field_obj.name, m2m_rel=rel_obj):
                yield rel_model

    def _get_extra_filters(self, fields: Iterable[str]) -> Generator[dict[str, bool], None, None]:
        for rel_model in self._get_m2m_relations_for(fields=fields):
            field_name = None
            for field in rel_model._meta.get_fields():
                # Locate the reverse-name of the field that points to the M2m through model
                if isinstance(field, models.ForeignKey) and field.related_model == self.model:
                    field_name = field.remote_field.name
                elif isinstance(field, models.ManyToOneRel) and field.field.related_model == self.model:
                    field_name = field.field.remote_field.name

                if field_name:
                    yield {f"{field_name}__deleted_at__isnull": True}
                    break


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
        qs = self.all_with_deleted() if "pk" in kwargs else self.all()

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
