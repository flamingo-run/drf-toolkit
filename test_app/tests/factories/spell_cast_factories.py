import factory

from test_app.models import SpellCast
from test_app.tests.factories.spell_factories import CombatSpellFactory, EnvironmentalSpellFactory
from test_app.tests.factories.wizard_factories import WizardFactory


class CombatSpellCastFactory(factory.django.DjangoModelFactory):
    wizard = factory.SubFactory(WizardFactory)
    spell = factory.SubFactory(CombatSpellFactory)
    is_successful = factory.Faker("pybool")

    class Meta:
        model = SpellCast


class EnvironmentSpellCastFactory(factory.django.DjangoModelFactory):
    wizard = factory.SubFactory(WizardFactory)
    spell = factory.SubFactory(EnvironmentalSpellFactory)
    is_successful = factory.Faker("pybool")

    class Meta:
        model = SpellCast
