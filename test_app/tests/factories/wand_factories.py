import factory

from test_app.models import Wand
from test_app.tests.factories.wizard_factories import WizardFactory


class WandFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("name")
    holder = factory.SubFactory(WizardFactory)

    class Meta:
        model = Wand
