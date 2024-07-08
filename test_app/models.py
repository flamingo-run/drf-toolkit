from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import DateTimeRangeField, RangeOperators
from django.db import models
from django.db.models import Value

from drf_kit.fields import SlugifyField
from drf_kit.models import (
    AvailabilityModel,
    BaseModel,
    InheritanceModel,
    OrderedModel,
    SoftDeleteAvailabilityModel,
    SoftDeleteInheritanceOrderedModel,
    SoftDeleteModel,
)
from test_app import managers
from test_app.storage import StoragePath


class Wizard(BaseModel):
    name = models.CharField(
        max_length=50,
    )
    age = models.IntegerField(
        null=True,
        blank=True,
    )
    minimum_age = models.GeneratedField(
        expression=Value(11),
        output_field=models.IntegerField(),
        db_persist=True,
    )
    is_half_blood = models.BooleanField(default=True)
    picture = models.FileField(
        **StoragePath.media_thumb(),
        null=True,
        blank=True,
    )
    extra_picture = models.FileField(
        **StoragePath.another_pic(),
        null=True,
        blank=True,
    )
    house = models.ForeignKey(
        to="test_app.House",
        related_name="wizards",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    spells = models.ManyToManyField(
        to="test_app.Spell",
        through="SpellCast",
        related_name="wizards",
    )
    received_letter_at = models.DateTimeField(
        blank=True,
        null=True,
    )


class House(BaseModel):
    name = models.CharField(
        max_length=50,
    )
    points_boost = models.DecimalField(
        default=1.0,
        decimal_places=2,
        max_digits=4,
    )


class Patronus(BaseModel):
    name = models.CharField(
        max_length=50,
    )
    color = models.CharField(
        max_length=50,
        null=True,
        db_column="colour",
    )
    wizard = models.OneToOneField(
        to="test_app.Wizard",
        on_delete=models.CASCADE,
    )
    memory = models.OneToOneField(
        to="test_app.Memory",
        on_delete=models.CASCADE,
        db_column="flashback_id",
        null=True,
    )


class Teacher(Wizard):
    is_ghost = models.BooleanField(
        default=False,
    )

    class Meta(Wizard.Meta):
        indexes = []

    objects = models.Manager()
    availables = managers.AvailableManager()


class Spell(InheritanceModel):
    name = models.CharField(
        max_length=50,
    )


class CombatSpell(Spell):
    is_attack = models.BooleanField(default=True)


class EnvironmentalSpell(Spell):
    pass


class SpellCast(BaseModel):
    wizard = models.ForeignKey(
        to="test_app.Wizard",
        on_delete=models.CASCADE,
        related_name="spell_casts",
    )
    spell = models.ForeignKey(
        to="test_app.Spell",
        on_delete=models.CASCADE,
        related_name="spell_casts",
    )
    is_successful = models.BooleanField(
        default=True,
    )


class Wand(BaseModel):
    name = models.CharField(
        max_length=50,
    )
    holder = models.ForeignKey(
        to="test_app.Wizard",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="wands",
    )

    class Meta(BaseModel.Meta):
        verbose_name = "varinha"


class Memory(SoftDeleteModel):
    owner = models.ForeignKey(
        to="test_app.Wizard",
        on_delete=models.CASCADE,
        related_name="memories",
    )
    description = models.TextField()


class TriWizardPlacement(OrderedModel):
    year = models.IntegerField()
    wizard = models.ForeignKey(
        to="test_app.Wizard",
        on_delete=models.CASCADE,
        related_name="placements",
    )
    prize = models.CharField(
        max_length=100,
    )

    order_with_respect_to = "year"

    class Meta(OrderedModel.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=["wizard", "year"],
                name="unique_wizard",
            ),
            models.UniqueConstraint(
                fields=["prize"],
                name="unique_prize",
            ),
        ]
        ordering = [
            "year",
            "order",
        ]

    def __str__(self):
        return f"Placement {self.pk}"


class Tale(SoftDeleteInheritanceOrderedModel):
    description = models.TextField()


class DarkTale(Tale):
    dark_level = models.IntegerField(default=0)

    class Meta(Tale.Meta):
        indexes = []


class HappyTale(Tale):
    laugh_level = models.IntegerField(default=0)

    class Meta(Tale.Meta):
        indexes = []


class RoomOfRequirement(AvailabilityModel):
    wizard = models.ForeignKey(
        to="test_app.Wizard",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )


class Newspaper(SoftDeleteAvailabilityModel):
    headline = models.CharField(max_length=30, default="?")


class Article(SoftDeleteModel):
    newspaper = models.ForeignKey(
        to="test_app.Newspaper",
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=30, default="?")


class News(SoftDeleteModel):
    newspaper = models.ForeignKey(
        to="test_app.Newspaper",
        on_delete=models.SET_NULL,
        null=True,
    )
    description = models.TextField(default="?")


class ExclusiveArticle(SoftDeleteModel):
    newspaper = models.OneToOneField(
        to="test_app.Newspaper",
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=30, default="?")
    slug = SlugifyField(null=True)


class ExclusiveNews(SoftDeleteModel):
    newspaper = models.OneToOneField(
        to="test_app.Newspaper",
        on_delete=models.SET_NULL,
        null=True,
    )
    description = models.TextField(default="?")


class BeastCategory(SoftDeleteModel):
    name = models.CharField(max_length=100)


class Beast(SoftDeleteModel):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    category = models.ForeignKey(to=BeastCategory, on_delete=models.CASCADE, null=True, related_name="beasts")
    is_active = models.BooleanField(default=True)

    class Meta(BaseModel.Meta):
        constraints = [
            models.UniqueConstraint(fields=["name", "age"], name="single-beast-per-year"),
            models.CheckConstraint(check=models.Q(age__gte=0), name="minimum-beast-age"),
        ]


class BeastOwnership(SoftDeleteModel):
    owner = models.ForeignKey(to="test_app.BeastOwner", on_delete=models.CASCADE)
    beast = models.ForeignKey(to="test_app.Beast", on_delete=models.CASCADE, related_name="ownerships")


class BeastOwner(SoftDeleteModel):
    name = models.CharField(max_length=100)
    beasts = models.ManyToManyField(to="test_app.Beast", through=BeastOwnership, related_name="owners")


class TrainingPitch(BaseModel):
    name = models.CharField(max_length=100)


class Reservation(BaseModel):
    wizard = models.ForeignKey(to="test_app.Wizard", on_delete=models.CASCADE, related_name="reservations")
    pitch = models.ForeignKey(to="test_app.TrainingPitch", on_delete=models.CASCADE, related_name="reservations")
    period = DateTimeRangeField()

    class Meta:
        constraints = [
            ExclusionConstraint(
                name="exclude_overlapping_reservations",
                expressions=[
                    ("period", RangeOperators.OVERLAPS),
                    ("pitch_id", RangeOperators.EQUAL),
                ],
            ),
        ]
