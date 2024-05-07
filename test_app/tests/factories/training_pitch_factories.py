from datetime import UTC

import factory
import faker

from test_app.models import Reservation, TrainingPitch
from test_app.tests.factories.wizard_factories import WizardFactory


class TrainingPitchFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("word")

    class Meta:
        model = TrainingPitch


class ReservationFactory(factory.django.DjangoModelFactory):
    pitch = factory.SubFactory(TrainingPitchFactory)
    wizard = factory.SubFactory(WizardFactory)
    period = (
        faker.Faker().date_time_between_dates(datetime_start="-1d", datetime_end="now", tzinfo=UTC),
        faker.Faker().date_time_between_dates(datetime_start="now", datetime_end="+1d", tzinfo=UTC),
    )

    class Meta:
        model = Reservation
