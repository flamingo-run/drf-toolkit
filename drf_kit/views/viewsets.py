import logging

from django.db.utils import IntegrityError
from rest_framework import status, viewsets
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response
from rest_framework_extensions.cache.mixins import BaseCacheResponseMixin

from drf_kit.cache import cache_response, cache_key_constructor
from drf_kit.exceptions import DuplicatedRecord

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
        SERIALIZERS = {
            "retrieve": self.serializer_detail_class,
            "create": self.serializer_create_class,
            "update": self.serializer_update_class or self.serializer_create_class,
        }
        action = self._get_action()

        klass = SERIALIZERS.get(action)

        if not klass:
            klass = super().get_serializer_class()
        return klass

    def get_serializer(self, *args, **kwargs):
        kwargs.update(self._get_serializer_extra_kwargs())
        kwargs.setdefault("context", self.get_serializer_context())
        return super().get_serializer(*args, **kwargs)

    def get_response_serializer_class(self):
        SERIALIZERS = {
            "retrieve": self.serializer_detail_class,
            "create": self.serializer_detail_class,
            "update": self.serializer_detail_class,
        }
        action = self._get_action()

        klass = SERIALIZERS.get(action)

        if not klass:
            klass = super().get_serializer_class()
        return klass

    def get_response_serializer(self, obj, **kwargs):
        kwargs.update(self._get_serializer_extra_kwargs())
        kwargs.setdefault("context", self.get_serializer_context())
        return self.get_response_serializer_class()(obj, **kwargs)

    def get_queryset(self, *args, **kwargs):
        QUERYSETS = {
            "retrieve": self.queryset_detail,
            "create": self.queryset_create,
            "update": self.queryset_update or self.queryset_create,
        }
        action = self._get_action()

        queryset = QUERYSETS.get(action)
        if not queryset:
            queryset = super().get_queryset(*args, **kwargs)
        else:
            queryset = queryset.all()
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
        headers = self.get_success_headers(serializer.data)

        data = self.get_response_serializer(obj).data
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
        try:
            # identical override of parent method, but returns the object
            return serializer.save()
        except IntegrityError as e:
            if DuplicatedRecord.verify(e):
                raise DuplicatedRecord(
                    serializer=serializer,
                    integrity_error=e,
                ) from e
            raise e

    def perform_update(self, serializer):
        # identical override of parent method, but returns the object
        return serializer.save()


class ModelViewSet(MultiSerializerMixin, viewsets.ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]


class ReadOnlyModelViewSet(MultiSerializerMixin, viewsets.ReadOnlyModelViewSet):
    http_method_names = ["get", "head", "options"]


class CacheResponseMixin(BaseCacheResponseMixin):
    @cache_response(key_func=cache_key_constructor)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_response(key_func=cache_key_constructor)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class CachedModelViewSet(CacheResponseMixin, ModelViewSet):
    pass


class CachedReadOnlyModelViewSet(CacheResponseMixin, ReadOnlyModelViewSet):
    pass


class WriteOnlyModelViewSet(MultiSerializerMixin, viewsets.ModelViewSet):
    http_method_names = ["post", "patch", "delete"]


class UpsertMixin(MultiSerializerMixin):
    upsert_status_code = status.HTTP_200_OK

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except DuplicatedRecord as e:
            instance = self.get_queryset().get(e.get_filter())
            return self.upsert(instance=instance, data=request.data, *args, **kwargs)

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
        SERIALIZERS = {
            "retrieve": self.serializer_detail_class,
            "create": self.serializer_list_class,
            "update": self.serializer_list_class,
        }
        action = self._get_action()

        klass = SERIALIZERS.get(action)

        if not klass:
            klass = super().get_serializer_class()
        return klass

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed(method="patch")
