import factory

from test_app.models import CombatSpell, EnvironmentalSpell, Spell


class SpellFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("word")

    class Meta:
        model = Spell


class CombatSpellFactory(SpellFactory):
    is_attack = factory.Faker("pybool")

    class Meta:
        model = CombatSpell


class EnvironmentalSpellFactory(SpellFactory):
    class Meta:
        model = EnvironmentalSpell
