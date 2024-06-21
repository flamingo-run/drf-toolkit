import functools

from django.db.models import Q
from django.forms import IntegerField
from django.http import QueryDict
from django_filters import MultipleChoiceFilter
from django_filters.fields import MultipleChoiceField
from django_filters.rest_framework import DjangoFilterBackend, Filter, FilterSet
from rest_framework.exceptions import ValidationError


class FilterBackend(DjangoFilterBackend):
    def filter_queryset(self, request, queryset, view):
        try:
            return super().filter_queryset(request, queryset, view)
        except (ValueError, AttributeError) as exc:
            raise ValidationError(str(exc)) from exc


class FilterInBodyBackend(DjangoFilterBackend):
    def get_filterset_kwargs(self, request, queryset, view):
        # Instead of data=request.query_params, we use data=request.data
        # The format must be as close as possible to the format of query_params (i.e. QueryDict)
        # so filter backends won't know the difference

        request_data = request.data.copy() or {}
        if isinstance(request_data, QueryDict):
            query = request_data
        elif isinstance(request_data, dict):
            query = self.dict_to_query(body=request_data)
        else:
            raise TypeError("request.data must be present")
        return super().get_filterset_kwargs(request, queryset, view) | {
            "data": query,
        }

    @classmethod
    def dict_to_query(cls, body: dict) -> QueryDict:
        query = QueryDict(mutable=True)
        for key, value in body.items():
            if isinstance(value, list):
                query.setlist(key, value)
            else:
                query[key] = value
        return query


class IntBooleanFilter(Filter):
    field_class = IntegerField

    @staticmethod
    def get_logic(value):
        logic = None
        if value == 1:
            logic = True
        elif value == 0:
            logic = False
        return logic

    def filter(self, qs, value):
        logic = self.get_logic(value=value)
        if logic is not None:
            return qs.filter(**{self.field_name: logic})
        return qs


class BaseFilterSet(FilterSet):
    def __init__(self, *args, data=None, **kwargs):
        if data is not None:
            data = data.copy()

            for name, filter_obj in self.base_filters.items():
                initial = filter_obj.extra.get("initial", None)
                if not data.get(name) and initial is not None:
                    data[name] = initial
                    if callable(initial):
                        data[name] = initial(request=kwargs["request"])

        super().__init__(data, *args, **kwargs)


class _OpenChoiceField(MultipleChoiceField):
    def valid_value(self, value):
        return True

    def clean(self, value):
        # when the value is set by Field.initial, it turns into a list of lists because each
        # field in the query parameters (set up at the Django view layer) defaults to being a list
        value = value[0] if value and isinstance(value, list) and isinstance(value[0], list) else value
        return super().clean(value)


class AnyOfFilter(MultipleChoiceFilter):
    field_class = _OpenChoiceField

    def filter(self, qs, value):
        if not value:
            return qs

        if self.is_noop(qs, value):
            return qs

        if not self.conjoined:
            predicate = {f"{self.field_name}__in": value}
            query_filter = Q(**predicate)
            qs = self.get_method(qs)(query_filter)

        return qs.distinct() if self.distinct else qs


class AllOfFilter(MultipleChoiceFilter):
    field_class = _OpenChoiceField

    def __init__(self, *args, **kwargs):
        if not kwargs.get("conjoined", True):
            raise ValueError("AllOfFilter must be conjoined=True")
        else:
            kwargs.setdefault("conjoined", True)
        super().__init__(*args, **kwargs)


class AnyOfOrNullFilter(MultipleChoiceFilter):
    NULL_VALUE = "null"
    field_class = _OpenChoiceField

    def filter(self, qs, value):
        if not value:
            return qs

        if self.is_noop(qs, value):
            return qs

        if not self.conjoined:
            filters = []

            if self.NULL_VALUE in value:
                predicate = {f"{self.field_name}__isnull": True}
                filters.append(Q(**predicate))
                value = [i for i in value if i != self.NULL_VALUE]

            if value:
                predicate = {f"{self.field_name}__in": value}
                filters.append(Q(**predicate))

            query_filter = functools.reduce((lambda a, b: a | b), filters)
            qs = self.get_method(qs)(query_filter)

        return qs.distinct() if self.distinct else qs


class IncludeUnavailableFilterSet(BaseFilterSet):
    include_unavailable = IntBooleanFilter(method="filter_include_unavailable", initial=0)

    def filter_include_unavailable(self, qs, name, value):
        available = self.Meta.model.availables.get_filter()

        boolean_value = IntBooleanFilter.get_logic(value)
        if boolean_value is None or boolean_value is True:
            return qs
        filtering = available
        return qs.filter(filtering).distinct()

    class Meta:
        model = None
