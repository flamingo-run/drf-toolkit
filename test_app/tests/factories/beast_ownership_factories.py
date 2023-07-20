import factory

from test_app.models import BeastOwnership


class BeastOwnershipFactory(factory.django.DjangoModelFactory):
    owner = factory.SubFactory("test_app.tests.factories.beast_owner_factories.BeastOwnerFactory")
    beast = factory.SubFactory("test_app.tests.factories.beast_factories.BeastFactory")

    class Meta:
        model = BeastOwnership
