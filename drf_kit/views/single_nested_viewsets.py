from django.http import Http404
from rest_framework import status
from rest_framework.response import Response

from drf_kit.views.nested_viewsets import NestedViewMixin
from drf_kit.views.viewsets import CachedReadOnlyModelViewSet, CacheResponseMixin, ModelViewSet, ReadOnlyModelViewSet


class SingleNestedViewMixin(NestedViewMixin):
    http_method_names = [*ModelViewSet.http_method_names, "put"]

    def get_object(self):
        return self.filter_queryset(self.get_queryset()).first()

    # Single Object Actions (/resource/<id>)
    def retrieve(self, request, *args, **kwargs):
        return self.http_pk_not_allowed()

    def destroy(self, request, *args, **kwargs):
        return self.http_pk_not_allowed()

    def partial_update(self, request, *args, **kwargs):
        if self.detail:
            return self.http_pk_not_allowed()
        return super().partial_update(request, *args, **kwargs)

    def http_pk_not_allowed(self):
        error = {"error": "There's no need to provide a PK since there's no more than 1 object"}
        return Response(
            data=error,
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    # Collection Actions (/resource)
    def create(self, request, **kwargs):
        instance = self.get_object()
        if instance:
            error = {"error": "Already exists and only one is allowed." " Use PUT to override existing relationship."}
            return Response(status=status.HTTP_409_CONFLICT, data=error)

        return super().create(request, **kwargs)

    def delete(self, request, **kwargs):
        self.filter_queryset(self.get_queryset()).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request, **kwargs):
        obj = self.get_object()
        if obj is None:
            raise Http404()
        serializer = self.get_response_serializer(obj)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        # New verb PATCH used as default for collections
        # Makes the collection behave as a single object
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        # New verb PUT used as default for collections
        # Makes the collection behave as a single object
        # and removes the previous before adding a new one
        if self.detail:
            return self.http_pk_not_allowed()
        instance = self.get_object()
        if instance:
            instance.delete()
            status_code = status.HTTP_200_OK
        else:
            status_code = status.HTTP_201_CREATED

        # Pretty similar to .create, but with dynamic status code
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        data = self.get_response_serializer(obj).data
        return Response(data, status=status_code, headers=headers)


class SingleNestedModelViewSet(SingleNestedViewMixin, ModelViewSet):
    pass


class CachedSingleNestedModelViewSet(CacheResponseMixin, SingleNestedModelViewSet):
    pass


class ReadOnlySingleNestedModelViewSet(SingleNestedViewMixin, ReadOnlyModelViewSet):
    pass


class CachedReadOnlySingleNestedModelViewSet(SingleNestedViewMixin, CachedReadOnlyModelViewSet):
    pass
