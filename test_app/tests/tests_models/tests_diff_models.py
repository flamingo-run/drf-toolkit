from django.core.files.uploadedfile import SimpleUploadedFile

from drf_kit.tests import BaseApiTest
from test_app.models import Wizard
from test_app.tests.factories.house_factories import HouseFactory
from test_app.tests.factories.wizard_factories import WizardFactory


class TestModelDiff(BaseApiTest):
    def test_created(self):
        wizard = Wizard(
            name="Harry Potter",
        )

        self.assertEqual({}, wizard._diff)
        self.assertFalse(wizard._has_changed)

    def test_updated(self):
        wizard = Wizard(
            name="Harry Potter",
            age=12,
        )

        wizard.age = 13
        expected_diff = {
            "age": (12, 13),
        }
        self.assertEqual(expected_diff, wizard._diff)
        self.assertTrue(wizard._has_changed)

    def test_not_updated(self):
        wizard = Wizard(
            name="Harry Potter",
            age=12,
        )

        wizard.age = 666
        wizard.age = 12

        self.assertEqual({}, wizard._diff)
        self.assertFalse(wizard._has_changed)

    def test_deleted(self):
        wizard = WizardFactory(id=100)
        wizard.delete()
        expected_diff = {
            "id": (100, None),
        }

        self.assertEqual(expected_diff, wizard._diff)
        self.assertTrue(wizard._has_changed)

    def test_updated_special_fields(self):
        house_a = HouseFactory(id=100)
        house_b = HouseFactory(id=200)

        old_file = SimpleUploadedFile("pre-harry.jpg", "○-○".encode())
        new_file = SimpleUploadedFile("new-harry.jpg", "○⚡︎○".encode())

        wizard = WizardFactory(
            name="Harry Potter",
            age=12,
            picture=old_file,
            house=house_a,
        )

        old_url = wizard.picture.url

        wizard.house = house_b
        wizard.picture = new_file

        new_url = wizard.picture.url

        self.assertTrue(wizard._has_changed)

        self.assertEqual((100, 200), wizard._diff["house_id"])
        self.assertEqual(old_url.removeprefix("/"), wizard._diff["picture"][0])
        self.assertEqual(new_url.removeprefix("/"), wizard._diff["picture"][1])

    def test_no_deferred_fields(self):
        with self.assertNumQueries(2):
            WizardFactory(name="Harry Potter", age=12)

        with self.assertNumQueries(1):
            # 1 SELECT with only
            wizard = Wizard.objects.first()

        with self.assertNumQueries(0):
            diff = wizard._diff

        expected_diff = {}
        self.assertEqual(expected_diff, diff)
        self.assertFalse(wizard._has_changed)

    def test_deferred_fields(self):
        with self.assertNumQueries(2):
            WizardFactory(name="Harry Potter", age=12)

        with self.assertNumQueries(2):
            # 1 SELECT with only
            # 1 SELECT with all fields (diff model)
            wizard = Wizard.objects.only("name").first()

        with self.assertNumQueries(0):
            diff = wizard._diff

        expected_diff = {}
        self.assertEqual(expected_diff, diff)
        self.assertFalse(wizard._has_changed)
