import factory

from test_app.models import BeastOwner


class BeastOwnerFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("name")

    class Meta:
        model = BeastOwner
