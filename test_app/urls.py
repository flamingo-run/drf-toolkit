from rest_framework.routers import DefaultRouter

from test_app import views

router = DefaultRouter(trailing_slash=False)

router.register(
    r"wizards",
    views.WizardViewSet,
    "wizard",
)

router.register(
    r"houses",
    views.HouseViewSet,
    "house",
)

router.register(
    r"teachers",
    views.TeacherViewSet,
    "teacher",
)

router.register(
    r"spells",
    views.SpellViewSet,
    "spell",
)

router.register(
    r"spells-light",
    views.SpellLightViewSet,
    "spell-light",
)

router.register(
    r"wizards/(?P<wizard_id>[^/.]+)/patronus",
    views.WizardPatronusViewSet,
    "wizard-to-patronus",
)

router.register(
    r"houses/(?P<house_id>[^/.]+)/wizards",
    views.HouseWizardsViewSet,
    "house-to-wizard",
)

router.register(
    r"spell-casts",
    views.SpellCastViewSet,
    "spell-cast",
)

router.register(
    r"memories",
    views.MemoryViewSet,
    "memories",
)
router.register(
    r"wizards/(?P<owner_id>[^/.]+)/memories",
    views.WizardToMemoryViewSet,
    "wizard-to-memories",
)

router.register(
    r"tri-wizard-placements",
    views.TriWizardPlacementViewSet,
    "tri-wizard-placements",
)

router.register(
    r"houses-bulk",
    views.HouseBulkViewSet,
    "house-bulk",
)

router.register(
    r"wands",
    views.WandViewSet,
    "wand",
)

router.register(
    r"beasts",
    views.BeastViewSet,
    "beast",
)

router.register(
    r"wizards-custom-filter",
    views.WizardCustomFilterViewSet,
    "wizard-custom-filter",
)

router.register(
    r"reservations",
    views.ReservationViewSet,
    "reservation",
)

router.register(
    r"training-pitches",
    views.TrainingPitchViewSet,
    "training-pitches",
)

urlpatterns = router.urls
