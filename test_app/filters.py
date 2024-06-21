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

    class Meta:
        model = models.Wizard
        fields = ["spell_name"]


class TrainingPitchFilterSet(filters.BaseFilterSet):
    name = filters.AnyOfFilter(initial=["Poppins"])

    class Meta:
        model = models.TrainingPitch
        fields = ["name"]
