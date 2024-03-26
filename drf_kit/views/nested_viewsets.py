import logging

from django.db.models import QuerySet
from django.http import Http404
from rest_framework.exceptions import ValidationError

from drf_kit import UNSET
from drf_kit.views.viewsets import CachedReadOnlyModelViewSet, CacheResponseMixin, ModelViewSet, ReadOnlyModelViewSet

logger = logging.getLogger(__name__)


class NestedViewMixin:
    queryset_nest: QuerySet = UNSET
    pk_field_nest: str = "pk"
    lookup_url_kwarg_nest: str = UNSET
    lookup_field_nest: str = UNSET
    serializer_field_nest: str = UNSET

    def __init__(self, *args, **kwargs):
        if self.queryset_nest is UNSET:
            raise NotImplementedError("NestedViewSet must contain a queryset_nest")
        if self.lookup_url_kwarg_nest is UNSET and self.lookup_field_nest is UNSET:
            raise NotImplementedError("NestedViewSet must contain either lookup_url_kwarg_nest or lookup_field_nest")
        if self.lookup_field_nest is UNSET:
            self.lookup_field_nest = self.lookup_url_kwarg_nest
        if self.lookup_url_kwarg_nest is UNSET:
            self.lookup_url_kwarg_nest = self.lookup_field_nest
        if self.serializer_field_nest is UNSET:
            self.serializer_field_nest = self.lookup_field_nest

        super().__init__(*args, **kwargs)

    def get_serializer(self, *args, **kwargs):
        if "data" in kwargs:
            # The data parameter might be a QueryDict (immutable),
            # so we assure it's a common dict (mutable) to add custom data
            kwargs["data"] = dict(kwargs["data"].items())

            # Proactively add the parent field value extracted from the URL to re-use serializers.
            # Avoid passing it by context and creating a new serializer
            # capable of reading the context
            nest_pk = self.get_nest_object().pk
            if self.lookup_field_nest in kwargs["data"]:
                provided_nest_pk = kwargs["data"][self.serializer_field_nest]
                if str(provided_nest_pk) != str(nest_pk):
                    raise ValidationError(
                        f"{self.serializer_field_nest} provided in the body ({provided_nest_pk})"
                        f"differs from the URL's ({nest_pk}). "
                        f"You can omit it from the request body.",
                    )
            kwargs["data"][self.serializer_field_nest] = nest_pk
        return super().get_serializer(*args, **kwargs)

    def get_nest_object(self):
        try:
            pk = self.kwargs[self.lookup_url_kwarg_nest]
        except KeyError as exc:
            raise ValueError(f"{self.lookup_url_kwarg_nest} not found in {self.kwargs}") from exc

        try:
            return self.queryset_nest.get(**{self.pk_field_nest: pk})
        except self.queryset_nest.model.DoesNotExist as exc:
            model_name = self.queryset_nest.model
            raise Http404(f"{model_name} with ID {pk} not found") from exc
        except ValueError as exc:
            raise ValidationError(exc) from exc

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset()
        return queryset.filter(**{self.lookup_field_nest: self.get_nest_object().pk})


class NestedModelViewSet(NestedViewMixin, ModelViewSet):
    pass


class CachedNestedModelViewSet(CacheResponseMixin, NestedModelViewSet):
    pass


class ReadOnlyNestedModelViewSet(NestedViewMixin, ReadOnlyModelViewSet):
    pass


class CachedReadOnlyNestedModelViewSet(NestedViewMixin, CachedReadOnlyModelViewSet):
    pass


class WriteOnlyNestedModelViewSet(NestedViewMixin, ModelViewSet):
    http_method_names = ["post", "patch", "delete"]
