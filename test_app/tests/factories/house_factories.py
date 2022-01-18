import factory

from test_app.models import House


class HouseFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("name")
    points_boost = 1.0

    class Meta:
        model = House
