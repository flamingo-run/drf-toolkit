from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from drf_kit import exceptions
from drf_kit.tests import BaseApiTest
from test_app.models import (
    Wizard,
    Spell,
    CombatSpell,
    EnvironmentalSpell,
    Memory,
)
from test_app.tests.tests_base import HogwartsTestMixin
from test_app.tests.factories.memory_factories import MemoryFactory
from test_app.tests.factories.wizard_factories import WizardFactory
from test_app.tests.factories.spell_factories import SpellFactory, EnvironmentalSpellFactory, CombatSpellFactory
from test_app.tests.factories.tri_wizard_placement_factories import TriWizardPlacementFactory
from test_app.tests.factories.house_factories import HouseFactory


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

        self.assertEqual((100, 200), wizard._diff["house"])
        self.assertEqual(old_url, wizard._diff["picture"][0])
        self.assertEqual(new_url, wizard._diff["picture"][1])


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

        with self.assertRaises(ValidationError):
            WizardFactory(
                id=100,
                name="Harry Potter",
                picture=a_file,
            )

        self.assertFalse(Wizard.objects.exists())


class TestMultiModel(BaseApiTest):
    def test_create_parent_model(self):
        spell = SpellFactory(name="Leviosa")
        self.assertEqual("spell", spell.type)

        self.assertFalse(EnvironmentalSpell.objects.exists())
        self.assertFalse(CombatSpell.objects.exists())

    def test_create_child_model(self):
        e_spell = EnvironmentalSpellFactory(name="Leviosa")
        self.assertEqual("environmentalspell", e_spell.type)

        c_spell = CombatSpellFactory(name="Petrificus")
        self.assertEqual("combatspell", c_spell.type)

        spells = Spell.objects.all()
        self.assertEqual(2, spells.count())


class TestSoftDeleteModel(HogwartsTestMixin, BaseApiTest):
    def test_delete_model(self):
        memory = MemoryFactory()
        self.assertIsNone(memory.deleted_at)

        memory.delete()
        memory.refresh_from_db()
        self.assertIsNotNone(memory.deleted_at)

    def test_undelete_model(self):
        memory = MemoryFactory()
        memory.delete()

        memory.undelete()
        memory.refresh_from_db()
        self.assertIsNone(memory.deleted_at)

    def test_update_deleted_using_model(self):
        new_description = "Parents fighting Voldemort"
        memory = MemoryFactory()
        memory.delete()

        memory.description = new_description

        with self.assertRaises(exceptions.UpdatingSoftDeletedException):
            memory.save()

        memory.refresh_from_db()
        self.assertNotEqual(new_description, memory.description)
        self.assertIsNotNone(memory.deleted_at)

    def test_update_deleted_using_queryset(self):
        new_description = "Parents fighting Voldemort"
        memory_a = MemoryFactory()
        memory_b = MemoryFactory()
        memory_b.delete()

        Memory.objects.all().update(description=new_description)

        memory_a.refresh_from_db()
        self.assertEqual(new_description, memory_a.description)

        memory_b.refresh_from_db()
        self.assertNotEqual(new_description, memory_b.description)

    def test_delete_using_model(self):
        memory = MemoryFactory()
        memory.delete()

        memory.refresh_from_db()
        self.assertIsNotNone(memory.deleted_at)

    def test_delete_using_queryset(self):
        memory_a = MemoryFactory()
        memory_b = MemoryFactory()

        Memory.objects.all().delete()

        memory_a.refresh_from_db()
        self.assertIsNotNone(memory_a.deleted_at)

        memory_b.refresh_from_db()
        self.assertIsNotNone(memory_b.deleted_at)

    def test_filter_by_default(self):
        memory_a = MemoryFactory()

        memory_b = MemoryFactory()
        memory_b.delete()

        memory_c = MemoryFactory()

        memories = Memory.objects.all()
        self.assertEqual(2, memories.count())

        [mem_c, mem_a] = memories
        self.assertEqual(memory_a, mem_a)
        self.assertEqual(memory_c, mem_c)

        deleted_memory = Memory.objects.get(pk=memory_b.pk)
        self.assertIsNotNone(deleted_memory.deleted_at)

    def test_filter_with_deleted(self):
        memory_a = MemoryFactory()

        memory_b = MemoryFactory()
        memory_b.delete()

        memory_c = MemoryFactory()

        memories = Memory.objects.all_with_deleted()
        self.assertEqual(3, memories.count())

        [mem_c, mem_b, mem_a] = memories
        self.assertEqual(memory_a, mem_a)
        self.assertEqual(memory_b, mem_b)
        self.assertEqual(memory_c, mem_c)

        deleted_memory = Memory.objects.get(pk=memory_b.pk)
        self.assertIsNotNone(deleted_memory.deleted_at)

    def test_get_referenced_deleted(self):
        wizard = WizardFactory()
        memory_a = MemoryFactory(owner=wizard)
        memory_b = MemoryFactory(owner=wizard)
        memory_b.delete()

        memories = wizard.memories.all()
        self.assertEqual(1, memories.count())
        self.assertEqual(memory_a, memories.first())

        memories = wizard.memories.all_with_deleted()
        self.assertEqual(2, memories.count())


class TestOrderedModel(HogwartsTestMixin, BaseApiTest):
    def setUp(self):
        super().setUp()
        self._set_up_wizards()

    def assertOrder(self, placement, expected_order):  # pylint:disable=invalid-name
        placement.refresh_from_db()
        self.assertEqual(expected_order, placement.order)

    def test_auto_order_when_adding(self):
        year = 1900

        placement_1 = TriWizardPlacementFactory(year=year, wizard=self.wizards[0], prize="rock")
        self.assertOrder(placement_1, 0)

        placement_2 = TriWizardPlacementFactory(
            year=year,
            wizard=self.wizards[1],
            prize="stone",
        )
        placement_3 = TriWizardPlacementFactory(
            year=year,
            wizard=self.wizards[2],
            prize="wand",
        )
        self.assertOrder(placement_1, 0)
        self.assertOrder(placement_2, 1)
        self.assertOrder(placement_3, 2)

        placement_4 = TriWizardPlacementFactory(
            year=year,
            wizard=self.wizards[3],
            prize="hug",
        )
        self.assertOrder(placement_1, 0)
        self.assertOrder(placement_2, 1)
        self.assertOrder(placement_3, 2)
        self.assertOrder(placement_4, 3)

        another_placement_1 = TriWizardPlacementFactory(
            year=2000,
            wizard=self.wizards[0],
        )
        self.assertOrder(another_placement_1, 0)

        self.assertOrder(placement_1, 0)
        self.assertOrder(placement_2, 1)
        self.assertOrder(placement_3, 2)
        self.assertOrder(placement_4, 3)

    def test_auto_order_when_removing(self):
        year = 1900

        placement_1 = TriWizardPlacementFactory(
            year=year,
            wizard=self.wizards[0],
            prize="rock",
        )
        placement_2 = TriWizardPlacementFactory(
            year=year,
            wizard=self.wizards[1],
            prize="stone",
        )
        placement_3 = TriWizardPlacementFactory(
            year=year,
            wizard=self.wizards[2],
            prize="wand",
        )
        self.assertOrder(placement_1, 0)
        self.assertOrder(placement_2, 1)
        self.assertOrder(placement_3, 2)

        placement_2.delete()

        placement_4 = TriWizardPlacementFactory(
            year=year,
            wizard=self.wizards[3],
            prize="hug",
        )
        self.assertOrder(placement_1, 0)
        self.assertOrder(placement_3, 1)
        self.assertOrder(placement_4, 2)

    def test_reordering_within_range(self):
        year = 1900

        placement_1 = TriWizardPlacementFactory(year=year, wizard=self.wizards[0], prize="rock")
        placement_2 = TriWizardPlacementFactory(year=year, wizard=self.wizards[1], prize="stone")
        placement_3 = TriWizardPlacementFactory(year=year, wizard=self.wizards[2], prize="wand")
        placement_4 = TriWizardPlacementFactory(year=year, wizard=self.wizards[3], prize="hug")

        placement_2.order = 3
        placement_2.save()

        for placement in [placement_1, placement_2, placement_3, placement_4]:
            placement.refresh_from_db()

        self.assertOrder(placement_1, 0)
        self.assertOrder(placement_2, 3)
        self.assertOrder(placement_3, 1)
        self.assertOrder(placement_4, 2)

    def test_reordering_after_range(self):
        year = 1900

        placement_1 = TriWizardPlacementFactory(year=year, wizard=self.wizards[0], prize="rock")
        placement_2 = TriWizardPlacementFactory(year=year, wizard=self.wizards[1], prize="stone")
        placement_3 = TriWizardPlacementFactory(year=year, wizard=self.wizards[2], prize="wand")
        placement_4 = TriWizardPlacementFactory(year=year, wizard=self.wizards[3], prize="hug")

        placement_3.order = 30
        placement_3.save()

        for placement in [placement_1, placement_2, placement_3, placement_4]:
            placement.refresh_from_db()

        self.assertOrder(placement_1, 0)
        self.assertOrder(placement_2, 1)
        self.assertOrder(placement_3, 3)
        self.assertOrder(placement_4, 2)

    def test_reordering_before_range(self):
        year = 1900

        placement_1 = TriWizardPlacementFactory(year=year, wizard=self.wizards[0], prize="rock")
        placement_2 = TriWizardPlacementFactory(year=year, wizard=self.wizards[1], prize="stone")
        placement_3 = TriWizardPlacementFactory(year=year, wizard=self.wizards[2], prize="wand")
        placement_4 = TriWizardPlacementFactory(year=year, wizard=self.wizards[3], prize="hug")

        placement_3.order = -3
        placement_3.save()

        for placement in [placement_1, placement_2, placement_3, placement_4]:
            placement.refresh_from_db()

        self.assertOrder(placement_1, 1)
        self.assertOrder(placement_2, 2)
        self.assertOrder(placement_3, 0)
        self.assertOrder(placement_4, 3)

    def test_reordering_to_zero(self):
        year = 1900

        placement_1 = TriWizardPlacementFactory(year=year, wizard=self.wizards[0], prize="rock")
        placement_2 = TriWizardPlacementFactory(year=year, wizard=self.wizards[1], prize="stone")
        placement_3 = TriWizardPlacementFactory(year=year, wizard=self.wizards[2], prize="wand")
        placement_4 = TriWizardPlacementFactory(year=year, wizard=self.wizards[3], prize="hug")

        placement_3.order = 0
        placement_3.save()

        for placement in [placement_1, placement_2, placement_3, placement_4]:
            placement.refresh_from_db()

        self.assertOrder(placement_1, 1)
        self.assertOrder(placement_2, 2)
        self.assertOrder(placement_3, 0)
        self.assertOrder(placement_4, 3)

    def test_create_within_range(self):
        year = 1900

        placement_1 = TriWizardPlacementFactory(year=year, wizard=self.wizards[0], prize="rock")
        placement_2 = TriWizardPlacementFactory(year=year, wizard=self.wizards[1], prize="stone")
        placement_3 = TriWizardPlacementFactory(year=year, wizard=self.wizards[2], prize="wand")
        placement_4 = TriWizardPlacementFactory(year=year, wizard=self.wizards[3], prize="hug", order=1)

        for placement in [placement_1, placement_2, placement_3, placement_4]:
            placement.refresh_from_db()

        self.assertOrder(placement_1, 0)
        self.assertOrder(placement_2, 2)
        self.assertOrder(placement_3, 3)
        self.assertOrder(placement_4, 1)

    def test_create_before_range(self):
        year = 1900

        placement_1 = TriWizardPlacementFactory(year=year, wizard=self.wizards[0], prize="rock")
        placement_2 = TriWizardPlacementFactory(year=year, wizard=self.wizards[1], prize="stone")
        placement_3 = TriWizardPlacementFactory(year=year, wizard=self.wizards[2], prize="wand")
        placement_4 = TriWizardPlacementFactory(year=year, wizard=self.wizards[3], prize="hug", order=-1)

        for placement in [placement_1, placement_2, placement_3, placement_4]:
            placement.refresh_from_db()

        self.assertOrder(placement_1, 1)
        self.assertOrder(placement_2, 2)
        self.assertOrder(placement_3, 3)
        self.assertOrder(placement_4, 0)
