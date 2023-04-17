import factory

from test_app.models import Beast


class BeastFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("name")
    age = factory.Faker("pyint", min_value=0)

    class Meta:
        model = Beast
