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


class WizardFilterSet(filters.BaseFilterSet):
    spell_name = filters.AllOfFilter(field_name="spell_casts__spell__name")
    any_spell_name = filters.AnyOfFilter(field_name="spell_casts__spell__name")

    class Meta:
        model = models.Wizard
        fields = ["spell_name"]


class TrainingPitchFilterSet(filters.BaseFilterSet):
    name = filters.AnyOfFilter(initial=["Poppins"])

    class Meta:
        model = models.TrainingPitch
        fields = ["name"]


def get_default_is_active(request) -> int:
    return 1


class BeastFilterSet(filters.BaseFilterSet):
    is_active = filters.IntBooleanFilter(initial=get_default_is_active)

    class Meta:
        model = models.Beast
        fields = ["is_active"]
