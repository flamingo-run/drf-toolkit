import factory

from test_app.models import Teacher
from test_app.tests.factories.wizard_factories import WizardFactory


class TeacherFactory(WizardFactory):
    is_ghost = factory.Faker("pybool")

    class Meta:
        model = Teacher
