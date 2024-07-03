import logging

from django.db import IntegrityError
from django.db.models import Model
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework_extensions.cache.mixins import BaseCacheResponseMixin

from drf_kit import exceptions, filters
from drf_kit.cache import body_cache_key_constructor, cache_response
from drf_kit.exceptions import ConflictException, DuplicatedRecord, ExclusionDuplicatedRecord

logger = logging.getLogger(__name__)


class MultiSerializerMixin:
    serializer_detail_class = None
    queryset_detail = None

    serializer_create_class = None
    queryset_create = None

    serializer_update_class = None
    queryset_update = None

    serializer_list_class = None

    def _get_serializer_extra_kwargs(self):
        return {}

    def get_serializer_class(self):
        serializers = {
            "retrieve": self.serializer_detail_class,
            "create": self.serializer_create_class,
            "update": self.serializer_update_class or self.serializer_create_class,
        }
        action = self._get_action()

        klass = serializers.get(action)

        if not klass:
            klass = super().get_serializer_class()
        return klass

    def get_serializer(self, *args, **kwargs):
        kwargs.update(self._get_serializer_extra_kwargs())
        kwargs.setdefault("context", self.get_serializer_context())
        return super().get_serializer(*args, **kwargs)

    def get_response_serializer_class(self):
        serializers = {
            "retrieve": self.serializer_detail_class,
            "create": self.serializer_detail_class,
            "update": self.serializer_detail_class,
        }
        action = self._get_action()

        klass = serializers.get(action)

        if not klass:
            klass = super().get_serializer_class()
        return klass

    def get_response_serializer(self, obj, **kwargs):
        kwargs.update(self._get_serializer_extra_kwargs())
        kwargs.setdefault("context", self.get_serializer_context())
        return self.get_response_serializer_class()(obj, **kwargs)

    def get_queryset(self, *args, **kwargs):
        querysets = {
            "retrieve": self.queryset_detail,
            "create": self.queryset_create,
            "update": self.queryset_update or self.queryset_create,
        }
        action = self._get_action()

        queryset = querysets.get(action)
        queryset = super().get_queryset(*args, **kwargs) if not queryset else queryset.all()
        return queryset

    def _get_action(self):
        def _is_request_to_detail_endpoint():
            if hasattr(self, "lookup_url_kwarg"):
                lookup = self.lookup_url_kwarg or self.lookup_field
            return bool(lookup and lookup in self.kwargs)

        verb = self.request.method.lower()
        if verb == "get" and _is_request_to_detail_endpoint():
            return "retrieve"
        if verb == "post":
            return "create"
        if verb == "patch":
            return "update"
        return "list"

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_response_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_response_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_response_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.perform_create(serializer)

        data = self.get_response_serializer(obj).data
        headers = self.get_success_headers(data)

        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        obj = self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        data = self.get_response_serializer(obj=obj).data
        return Response(data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        # identical override of parent method, but returns the object
        return serializer.save()

    def perform_update(self, serializer):
        # identical override of parent method, but returns the object
        return serializer.save()

    def get_exception_handler(self):
        return exceptions.custom_exception_handler


search_action = action(
    detail=False,
    methods=["post"],
    filter_backends=[filters.FilterInBodyBackend, *api_settings.DEFAULT_FILTER_BACKENDS],
)


class SearchMixin:
    @search_action
    def search(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ModelViewSet(MultiSerializerMixin, viewsets.ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]


class ReadOnlyModelViewSet(MultiSerializerMixin, viewsets.ReadOnlyModelViewSet):
    http_method_names = ["get", "head", "options"]


class NonDestructiveModelViewSet(ModelViewSet):
    http_method_names = ["get", "post", "patch", "head", "options"]


class CacheResponseMixin(BaseCacheResponseMixin):
    @cache_response()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_response()
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class CachedModelViewSet(CacheResponseMixin, ModelViewSet):
    pass


class CachedSearchableMixin(SearchMixin, CacheResponseMixin):
    @search_action
    @cache_response(key_func=body_cache_key_constructor)
    def search(self, request, *args, **kwargs):
        return super().search(request, *args, **kwargs)


class CachedSearchableModelViewSet(CachedSearchableMixin, ModelViewSet):
    pass


class CachedReadOnlyModelViewSet(CacheResponseMixin, ReadOnlyModelViewSet):
    pass


class CachedSearchableReadOnlyModelViewSet(CachedSearchableMixin, ReadOnlyModelViewSet):
    pass


class CachedNonDestructiveModelViewSet(CacheResponseMixin, NonDestructiveModelViewSet):
    pass


class CachedSearchableNonDestructiveModelViewSet(CachedSearchableMixin, NonDestructiveModelViewSet):
    pass


class WriteOnlyModelViewSet(MultiSerializerMixin, viewsets.ModelViewSet):
    http_method_names = ["post", "patch", "delete"]


class UpsertMixin(MultiSerializerMixin):
    upsert_status_code = status.HTTP_200_OK

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except (IntegrityError, ConflictException) as exc:
            instance = self.get_duplicated_record(
                model_klass=self.get_queryset().model, body=request.data, exception=exc
            )
            if not instance:
                raise
        return self.upsert(instance=instance, data=request.data, *args, **kwargs)

    def get_duplicated_record(self, model_klass: type[Model], body: dict, exception: Exception) -> Model | None:
        if isinstance(exception, IntegrityError):
            if DuplicatedRecord.verify(integrity_error=exception):
                error = DuplicatedRecord(model_klass=model_klass, body=body, integrity_error=exception)
            elif ExclusionDuplicatedRecord.verify(integrity_error=exception):
                error = ExclusionDuplicatedRecord(model_klass=model_klass, body=body, integrity_error=exception)
            else:
                return None
            return model_klass.objects.get(error.get_filter())
        if isinstance(exception, ConflictException):
            if len(exception.with_models) != 1:  # Upsert can only handle conflict with 1 model
                return None
            return exception.with_models[0]
        return None

    def upsert(self, instance, data, *args, **kwargs):
        partial = True
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        obj = self.perform_update(serializer)

        data = self.get_response_serializer(obj).data
        return Response(data, status=self.upsert_status_code)


class BulkMixin(MultiSerializerMixin):
    def _get_serializer_extra_kwargs(self):
        if self._get_action() != "retrieve":
            return {"many": True}
        return {}

    def get_response_serializer_class(self):
        serializers = {
            "retrieve": self.serializer_detail_class,
            "create": self.serializer_list_class,
            "update": self.serializer_list_class,
        }
        action = self._get_action()

        klass = serializers.get(action)

        if not klass:
            klass = super().get_serializer_class()
        return klass

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed(method="patch")
