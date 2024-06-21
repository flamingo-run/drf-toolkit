from rest_framework.fields import CharField, IntegerField, ListField

from drf_kit import serializers
from test_app import models


class HouseSerializer(serializers.BaseModelSerializer):
    class Meta(serializers.BaseModelSerializer.Meta):
        model = models.House
        fields = (
            "id",
            "name",
            "points_boost",
            "created_at",
        )
        read_only_fields = (
            "id",
            "created_at",
        )


class HouseStatsSerializer(HouseSerializer):
    wizard_count = IntegerField(read_only=True)

    class Meta(HouseSerializer.Meta):
        fields = (*HouseSerializer.Meta.fields, "wizard_count")


class WizardShortSerializer(serializers.BaseModelSerializer):
    class Meta(serializers.BaseModelSerializer.Meta):
        model = models.Wizard
        fields = (
            "name",
            "is_half_blood",
            "received_letter_at",
        )


class WizardSerializer(WizardShortSerializer):
    house_id = serializers.ForeignKeyField(queryset=models.House.objects.all())
    house = HouseSerializer(read_only=True)

    class Meta(WizardShortSerializer.Meta):
        fields = (
            *WizardShortSerializer.Meta.fields,
            "id",
            "created_at",
            "updated_at",
            "age",
            "picture",
            "house_id",
            "house",
        )


class WizardCreatorSerializer(serializers.BaseModelSerializer):
    class Meta(serializers.BaseModelSerializer.Meta):
        model = models.Wizard
        fields = (
            "name",
            "age",
            "is_half_blood",
        )


class WizardUpdaterSerializer(serializers.BaseModelSerializer):
    class Meta(serializers.BaseModelSerializer.Meta):
        model = models.Wizard
        fields = ("age",)


class PatronusSerializer(serializers.BaseModelSerializer):
    wizard_id = serializers.ForeignKeyField(queryset=models.Wizard.objects.all())
    wizard = WizardShortSerializer(read_only=True)

    class Meta(serializers.BaseModelSerializer.Meta):
        model = models.Patronus
        fields = (
            "wizard_id",
            "wizard",
            "id",
            "name",
            "color",
        )


class TeacherSerializer(WizardSerializer):
    class Meta(WizardSerializer.Meta):
        model = models.Teacher
        fields = (*WizardSerializer.Meta.fields, "is_ghost")


class SpellSerializer(serializers.BaseModelSerializer):
    class Meta(serializers.BaseModelSerializer.Meta):
        model = models.Spell
        fields = "__all__"


class SpellCastSerializer(serializers.BaseModelSerializer):
    wizard_id = serializers.ForeignKeyField(queryset=models.Wizard.objects.all())
    wizard = WizardSerializer(read_only=True)

    spell_id = serializers.ForeignKeyField(queryset=models.Spell.objects.all())
    spell = SpellSerializer(read_only=True)

    class Meta(serializers.BaseModelSerializer.Meta):
        model = models.SpellCast
        fields = (
            "id",
            "wizard_id",
            "wizard",
            "spell_id",
            "spell",
            "is_successful",
        )


class MemorySerializer(serializers.BaseModelSerializer):
    owner_id = serializers.ForeignKeyField(queryset=models.Wizard.objects.all(), write_only=False)

    class Meta(serializers.BaseModelSerializer.Meta):
        model = models.Memory
        fields = (
            "id",
            "owner_id",
            "description",
        )


class TriWizardPlacementSerializer(serializers.BaseModelSerializer):
    wizard_id = serializers.ForeignKeyField(queryset=models.Wizard.objects.all(), write_only=False)
    prize = CharField(write_only=True)

    class Meta(serializers.BaseModelSerializer.Meta):
        model = models.TriWizardPlacement
        fields = (
            "id",
            "wizard_id",
            "year",
            "prize",
        )


class WandSerializer(serializers.BaseModelSerializer):
    class Meta(serializers.BaseModelSerializer.Meta):
        model = models.Wand
        fields = (
            "id",
            "name",
        )


class BeastSerializer(serializers.BaseModelSerializer):
    class Meta(serializers.BaseModelSerializer.Meta):
        model = models.Beast
        fields = (
            "id",
            "name",
            "age",
        )


class ReservationSerializer(serializers.BaseModelSerializer):
    period = ListField(write_only=False)
    wizard_id = serializers.ForeignKeyField(queryset=models.Wizard.objects.all(), write_only=False)
    pitch_id = serializers.ForeignKeyField(queryset=models.TrainingPitch.objects.all(), write_only=False)

    class Meta(serializers.BaseModelSerializer.Meta):
        model = models.Reservation
        fields = (
            "id",
            "wizard_id",
            "pitch_id",
            "period",
        )


class TrainingPitchSerializer(serializers.BaseModelSerializer):
    class Meta(serializers.BaseModelSerializer.Meta):
        model = models.TrainingPitch
        fields = ("id",)
