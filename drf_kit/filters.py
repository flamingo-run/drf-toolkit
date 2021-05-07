from django.db.models import Q
from django.forms import IntegerField
from django_filters import MultipleChoiceFilter
from django_filters.fields import MultipleChoiceField
from django_filters.rest_framework import FilterSet, Filter, DjangoFilterBackend
from rest_framework.exceptions import ValidationError


class FilterBackend(DjangoFilterBackend):
    def filter_queryset(self, request, queryset, view):
        try:
            return super().filter_queryset(request, queryset, view)
        except (ValueError, AttributeError) as exc:
            raise ValidationError(str(exc)) from exc


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

            for name, filter_obj in self.base_filters.items():  # pylint: disable=no-member
                initial = filter_obj.extra.get("initial", None)
                if not data.get(name) and initial is not None:
                    data[name] = initial

        super().__init__(data, *args, **kwargs)


class _OpenChoiceField(MultipleChoiceField):
    def valid_value(self, value):
        return True


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
