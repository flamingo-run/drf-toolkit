from django.db.models import Count

from drf_kit.views import (
    CachedModelViewSet,
    ModelViewSet,
    NestedModelViewSet,
    SingleNestedModelViewSet,
    ReadOnlyModelViewSet,
    StatsViewMixin,
    WriteOnlyModelViewSet,
    WriteOnlyNestedModelViewSet,
    UpsertMixin,
)
from test_app import filters, models, serializers


class HouseViewSet(StatsViewMixin, ModelViewSet):
    queryset = models.House.objects.all()
    serializer_class = serializers.HouseSerializer
    serializer_stats_class = serializers.HouseStatsSerializer
    ordering_fields = ('name', 'id')
    search_fields = ['name']

    def add_stats_to_queryset(self, queryset):
        return queryset.annotate(
            wizard_count=Count('wizards__id'),
        )


class TeacherViewSet(CachedModelViewSet):
    queryset = models.Teacher.objects.all()
    serializer_class = serializers.TeacherSerializer
    filterset_class = filters.TeacherFilterSet
    ordering_fields = ('name', 'id')


class WizardViewSet(ModelViewSet):
    queryset = models.Wizard.objects.all()
    serializer_class = serializers.WizardShortSerializer

    queryset_detail = models.Wizard.objects.filter(age__gte=18)
    serializer_detail_class = serializers.WizardSerializer

    queryset_create = models.Wizard.objects.all()
    serializer_create_class = serializers.WizardCreatorSerializer

    queryset_update = models.Wizard.objects.filter(age__lte=18)
    serializer_update_class = serializers.WizardUpdaterSerializer


class HouseWizardsViewSet(NestedModelViewSet):
    queryset_nest = models.House.objects.all()
    lookup_url_kwarg_nest = 'house_id'

    queryset = models.Wizard.objects.all()
    serializer_class = serializers.WizardShortSerializer
    serializer_detail_class = serializers.WizardSerializer
    serializer_create_class = serializers.WizardSerializer
    serializer_update_class = serializers.WizardSerializer


class WizardPatronusViewSet(SingleNestedModelViewSet):
    queryset_nest = models.Wizard.objects.all()
    lookup_url_kwarg_nest = 'wizard_id'

    queryset = models.Patronus.objects.all()
    serializer_class = serializers.PatronusSerializer


class SpellViewSet(ReadOnlyModelViewSet):
    queryset = models.Spell.objects.all().order_by('name')
    serializer_class = serializers.SpellSerializer

    queryset_detail = models.Spell.objects.all()
    serializer_detail_class = serializers.SpellSerializer


class SpellCastViewSet(ModelViewSet):
    queryset = models.SpellCast.objects.all()
    serializer_class = serializers.SpellCastSerializer


class MemoryViewSet(WriteOnlyModelViewSet):
    queryset = models.Memory.objects.all()
    serializer_class = serializers.MemorySerializer


class WizardToMemoryViewSet(WriteOnlyNestedModelViewSet):
    queryset_nest = models.Wizard.objects.all()
    lookup_field_nest = 'owner_id'

    queryset = models.Memory.objects.all()
    serializer_class = serializers.MemorySerializer


class TriWizardPlacementViewSet(UpsertMixin, ModelViewSet):
    queryset = models.TriWizardPlacement.objects.all()
    serializer_class = serializers.TriWizardPlacementSerializer
