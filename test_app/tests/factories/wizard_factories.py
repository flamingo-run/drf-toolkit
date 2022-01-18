import factory

from test_app.models import Wizard


class WizardFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("name")
    age = factory.Faker("pyint")
    is_half_blood = factory.Faker("pybool")
    picture = factory.django.FileField(filename="wiz.jpg")
    extra_picture = factory.django.FileField(filename="more_wiz.jpg")
    house = None
    received_letter_at = factory.Faker("date_time")

    class Meta:
        model = Wizard
