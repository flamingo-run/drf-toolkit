import factory

from test_app.models import Memory
from test_app.tests.factories.wizard_factories import WizardFactory


class MemoryFactory(factory.django.DjangoModelFactory):
    description = factory.Faker("text")
    owner = factory.SubFactory(WizardFactory)

    class Meta:
        model = Memory
