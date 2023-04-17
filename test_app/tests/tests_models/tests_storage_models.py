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
        a_file = SimpleUploadedFile("wtf", b"42")

        with self.assertLogs(level="WARNING") as log:
            wizard = WizardFactory(
                id=100,
                name="Harry Potter",
                extra_picture=a_file,
            )
            [output] = log.output
        self.assertEqual("WARNING:root:Saving file without extension", output)

        self.assertTrue(Wizard.objects.exists())
        self.assertUUIDFilePath(
            prefix="wizard",
            name="wtf",
            extension="",
            pk=100,
            file=wizard.extra_picture,
        )
