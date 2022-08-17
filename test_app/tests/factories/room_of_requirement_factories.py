import factory

from test_app.models import RoomOfRequirement


class RoomOfRequirementFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RoomOfRequirement
