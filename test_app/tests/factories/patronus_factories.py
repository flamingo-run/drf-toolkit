import factory

from test_app.models import Patronus
from test_app.tests.factories.wizard_factories import WizardFactory


class PatronusFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("name")
    color = factory.Faker("word")
    wizard = factory.SubFactory(WizardFactory)

    class Meta:
        model = Patronus
