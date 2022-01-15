from django.db import models

from drf_kit.models import BaseModel, SoftDeleteModel, InheritanceModel, BaseOrderedModel
from test_app import managers
from test_app.storage import StoragePath

class Coordinates:
    def __init__(self, latitude, longitude):
        self.latitude = float(latitude)
        self.longitude = float(longitude)

    def default(self):
        return dict(longitude=self.longitude, latitude=self.latitude)

class CoordinatesField(models.CharField):
    def __init__(self,*args, **kwargs) -> None:
        kwargs.setdefault("max_length", 100)
        kwargs.setdefault("null", True)
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        if not value:
            return value
        return Coordinates(*value.split(','))

    def get_db_prep_save(self, value, *args, **kwargs):
        if not value:
            return None
        return f"{value['latitude']},{value['longitude']}"


class Wizard(BaseModel):
    name = models.CharField(
        max_length=50,
    )
    age = models.IntegerField(
        null=True,
        blank=True,
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
    coordinates = CoordinatesField()


class House(BaseModel):
    name = models.CharField(
        max_length=50,
    )
    points_boost = models.DecimalField(
        default=1.0,
        decimal_places=2,
        max_digits=4,
    )

    _PUBSUB_NAME = "team"


class Patronus(BaseModel):
    name = models.CharField(
        max_length=50,
    )
    color = models.CharField(
        max_length=50,
        null=True,
    )
    wizard = models.OneToOneField(
        to="test_app.Wizard",
        on_delete=models.CASCADE,
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


class TriWizardPlacement(BaseOrderedModel):
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

    class Meta(BaseOrderedModel.Meta):
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
