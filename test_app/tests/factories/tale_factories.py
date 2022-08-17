import factory

from test_app.models import DarkTale, HappyTale, Tale


class TaleFactory(factory.django.DjangoModelFactory):
    description = factory.Faker("text")

    class Meta:
        model = Tale


class DarkTaleFactory(TaleFactory):
    dark_level = factory.Faker("pyint")

    class Meta:
        model = DarkTale


class HappyTaleFactory(TaleFactory):
    laugh_level = factory.Faker("pyint")

    class Meta:
        model = HappyTale
