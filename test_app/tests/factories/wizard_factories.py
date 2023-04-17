from datetime import UTC, datetime

import factory
from factory.fuzzy import FuzzyDateTime

from test_app.models import Wizard


class WizardFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("name")
    age = factory.Faker("pyint")
    is_half_blood = factory.Faker("pybool")
    picture = factory.django.FileField(filename="wiz.jpg")
    extra_picture = factory.django.FileField(filename="more_wiz.jpg")
    house = None
    received_letter_at = FuzzyDateTime(datetime(2008, 1, 1, tzinfo=UTC))

    class Meta:
        model = Wizard
