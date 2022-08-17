from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from drf_kit.tests import BaseApiTest
from test_app.models import Wizard
from test_app.tests.factories.wizard_factories import WizardFactory


class TestModelStorage(BaseApiTest):
    def test_file_path(self):
        a_file = SimpleUploadedFile("./pics/harry.jpg", "○⚡︎○".encode())

        wizard = WizardFactory(
            id=100,
            name="Harry Potter",
            picture=a_file,
        )

        self.assertUUIDFilePath(
            prefix="wizard",
            name="thumb",
            extension="jpg",
            pk=100,
            file=wizard.picture,
        )

    def test_file_path_preserve_name(self):
        a_file = SimpleUploadedFile("./pics/harryyyyy.cdr", "○⚡︎○".encode())

        wizard = WizardFactory(
            id=100,
            name="Harry Potter",
            extra_picture=a_file,
        )

        self.assertUUIDFilePath(
            prefix="wizard",
            name="harryyyyy",
            extension="cdr",
            pk=100,
            file=wizard.extra_picture,
        )

    def test_invalid_file_path(self):
        a_file = SimpleUploadedFile("wtf", "42".encode())

        with self.assertRaisesRegex(ValidationError, "Filename must have and extension"):
            WizardFactory(
                id=100,
                name="Harry Potter",
                extra_picture=a_file,
            )

        self.assertFalse(Wizard.objects.exists())
