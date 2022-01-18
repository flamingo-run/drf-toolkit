import factory

from test_app.models import TriWizardPlacement
from test_app.tests.factories.wizard_factories import WizardFactory


class TriWizardPlacementFactory(factory.django.DjangoModelFactory):
    year = factory.Faker("pyint")
    prize = factory.Faker("word")
    wizard = factory.SubFactory(WizardFactory)

    class Meta:
        model = TriWizardPlacement
