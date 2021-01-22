from rest_framework.exceptions import ValidationError

from drf_kit.filters import IntBooleanFilter


class StatsViewMixin:
    serializer_stats_class = None

    @property
    def with_stats(self):
        stats_param = self.request.query_params.get('stats', '0')
        try:
            stats_value = int(stats_param)
        except ValueError as e:
            raise ValidationError({'stats': "Stats parameter must be an integer"}) from e
        return IntBooleanFilter.get_logic(stats_value)

    def get_queryset(self):
        qs = super().get_queryset()
        if self.with_stats:
            qs = self.add_stats_to_queryset(queryset=qs)
        return qs

    def get_serializer_class(self):
        klass = getattr(self, 'serializer_stats_class', None)
        if not klass or not self.with_stats:
            klass = super().get_serializer_class()
        return klass

    def add_stats_to_queryset(self, queryset):
        raise NotImplementedError()
