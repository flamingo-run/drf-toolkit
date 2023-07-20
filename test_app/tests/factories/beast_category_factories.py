import factory

from test_app.models import BeastCategory


class BeastCategoryFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("name")

    class Meta:
        model = BeastCategory
