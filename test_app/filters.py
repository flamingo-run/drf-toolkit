from drf_kit import filters
from test_app import models


class TeacherFilterSet(filters.IncludeUnavailableFilterSet):
    id = filters.AnyOfFilter()

    class Meta:
        model = models.Teacher
        fields = [
            "id",
            "name",
            "include_unavailable",
            "is_half_blood",
        ]


class WandFilterSet(filters.BaseFilterSet):
    holder_id = filters.AnyOfOrNullFilter()

    class Meta:
        model = models.Wand
        fields = ["holder_id"]
