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
    DarkTale,
    Tale,
)
from test_app import models
from test_app.tests.tests_base import HogwartsTestMixin
from test_app.tests.factories.tale_factories import DarkTaleFactory, HappyTaleFactory, TaleFactory
from test_app.tests.factories.memory_factories import MemoryFactory
from test_app.tests.factories.wizard_factories import WizardFactory
from test_app.tests.factories.spell_factories import SpellFactory, EnvironmentalSpellFactory, CombatSpellFactory
from test_app.tests.factories.tri_wizard_placement_factories import TriWizardPlacementFactory
from test_app.tests.factories.house_factories import HouseFactory
from test_app.tests.factories.patronus_factories import PatronusFactory


class TestModelDict(BaseApiTest):
    def test_field(self):
        wizard = WizardFactory(name="Harry")
        patronus = PatronusFactory(name="Stag", wizard=wizard)

        generated_dict = patronus._dict
        self.assertEqual(patronus.name, generated_dict["name"])

        models.Patronus(**generated_dict)

    def test_fk_generated_with_id(self):
        wizard = WizardFactory(name="Harry")
        patronus = PatronusFactory(name="Stag", wizard=wizard)

        generated_dict = patronus._dict
        self.assertEqual(wizard.pk, generated_dict["wizard_id"])

        models.Patronus(**generated_dict)


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

    def test_updated_fk(self):
        harry = WizardFactory(
            name="Harry Potter",
            age=12,
        )

        james = WizardFactory(
            name="James Potter",
            age=21,
        )

        patronus = PatronusFactory(name="Stag", wizard=james)
        patronus.refresh_from_db()

        patronus.wizard = harry

        expected_diff = {
            "wizard_id": (james.pk, harry.pk),
        }
        self.assertEqual(expected_diff, patronus._diff)
        self.assertTrue(patronus._has_changed)

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

        old_url = wizard.picture.url.removeprefix("/")

        wizard.house = house_b
        wizard.picture = new_file

        new_url = wizard.picture.url.removeprefix("/")

        self.assertTrue(wizard._has_changed)

        self.assertEqual((100, 200), wizard._diff["house_id"])
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

    def test_file_path_with_default_extension(self):
        a_file = SimpleUploadedFile("./pics/harry", "○⚡︎○".encode())

        wizard = WizardFactory(
            id=100,
            name="Harry Potter",
            picture=a_file,
        )

        self.assertUUIDFilePath(
            prefix="wizard",
            name="thumb",
            extension="jpeg",
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
                extra_picture=a_file,
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
        memory.refresh_from_db()

        memory.undelete()
        memory.refresh_from_db()
        self.assertIsNone(memory.deleted_at)

    def test_update_deleted_using_model(self):
        new_description = "Parents fighting Voldemort"
        memory = MemoryFactory()
        memory.delete()
        memory.refresh_from_db()

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


class TestSoftDeleteInheritanceOrderedModel(HogwartsTestMixin, BaseApiTest):
    # ORDERING FEATURES
    def assertOrder(self, obj, expected_order):  # pylint:disable=invalid-name
        obj.refresh_from_db()
        self.assertEqual(expected_order, obj.order)

    def test_auto_order_when_adding(self):
        tale_a = DarkTaleFactory()
        self.assertOrder(tale_a, 0)

        tale_b = DarkTaleFactory()
        tale_c = DarkTaleFactory()
        self.assertOrder(tale_a, 0)
        self.assertOrder(tale_b, 1)
        self.assertOrder(tale_c, 2)

        tale_d = DarkTaleFactory()
        self.assertOrder(tale_a, 0)
        self.assertOrder(tale_b, 1)
        self.assertOrder(tale_c, 2)
        self.assertOrder(tale_d, 3)

        tale_e = HappyTaleFactory()
        self.assertOrder(tale_a, 0)
        self.assertOrder(tale_b, 1)
        self.assertOrder(tale_c, 2)
        self.assertOrder(tale_d, 3)
        self.assertOrder(tale_e, 0)

    def test_auto_order_when_removing(self):
        tale_a = DarkTaleFactory()
        tale_b = DarkTaleFactory()
        tale_c = DarkTaleFactory()
        self.assertOrder(tale_a, 0)
        self.assertOrder(tale_b, 1)
        self.assertOrder(tale_c, 2)

        tale_b.delete()
        self.assertOrder(tale_a, 0)
        self.assertOrder(tale_c, 1)

    def test_reordering_within_range(self):
        tale_a = DarkTaleFactory()
        tale_b = DarkTaleFactory()
        tale_c = DarkTaleFactory()
        tale_d = DarkTaleFactory()

        tale_b.order = 2
        tale_b.save()
        self.assertOrder(tale_a, 0)
        self.assertOrder(tale_b, 2)
        self.assertOrder(tale_c, 1)
        self.assertOrder(tale_d, 3)

    def test_reordering_after_range(self):
        tale_a = DarkTaleFactory()
        tale_b = DarkTaleFactory()
        tale_c = DarkTaleFactory()
        tale_d = DarkTaleFactory()

        tale_b.order = 30
        tale_b.save()
        self.assertOrder(tale_a, 0)
        self.assertOrder(tale_b, 3)
        self.assertOrder(tale_c, 1)
        self.assertOrder(tale_d, 2)

    def test_reordering_before_range(self):
        tale_a = DarkTaleFactory()
        tale_b = DarkTaleFactory()
        tale_c = DarkTaleFactory()
        tale_d = DarkTaleFactory()

        tale_b.order = -30
        tale_b.save()
        self.assertOrder(tale_a, 1)
        self.assertOrder(tale_b, 0)
        self.assertOrder(tale_c, 2)
        self.assertOrder(tale_d, 3)

    def test_reordering_to_zero(self):
        tale_a = DarkTaleFactory()
        tale_b = DarkTaleFactory()
        tale_c = DarkTaleFactory()
        tale_d = DarkTaleFactory()

        tale_b.order = 0
        tale_b.save()
        self.assertOrder(tale_a, 1)
        self.assertOrder(tale_b, 0)
        self.assertOrder(tale_c, 2)
        self.assertOrder(tale_d, 3)

    def test_create_within_range(self):
        tale_a = DarkTaleFactory()
        tale_b = DarkTaleFactory()
        tale_c = DarkTaleFactory()
        tale_d = DarkTaleFactory(order=2)
        self.assertOrder(tale_a, 0)
        self.assertOrder(tale_b, 1)
        self.assertOrder(tale_c, 3)
        self.assertOrder(tale_d, 2)

    def test_create_before_range(self):
        tale_a = DarkTaleFactory()
        tale_b = DarkTaleFactory()
        tale_c = DarkTaleFactory()
        tale_d = DarkTaleFactory(order=-30)
        self.assertOrder(tale_a, 1)
        self.assertOrder(tale_b, 2)
        self.assertOrder(tale_c, 3)
        self.assertOrder(tale_d, 0)

    def test_create_after_range(self):
        tale_a = DarkTaleFactory()
        tale_b = DarkTaleFactory()
        tale_c = DarkTaleFactory()
        tale_d = DarkTaleFactory(order=30)
        self.assertOrder(tale_a, 0)
        self.assertOrder(tale_b, 1)
        self.assertOrder(tale_c, 2)
        self.assertOrder(tale_d, 3)

    # SOFT-DELETE FEATURES
    def test_delete_model(self):
        tale = DarkTaleFactory()
        self.assertIsNone(tale.deleted_at)

        tale.delete()
        tale.refresh_from_db()
        self.assertIsNotNone(tale.deleted_at)

    def test_undelete_model(self):
        tale = DarkTaleFactory()
        tale.delete()

        tale.undelete()
        tale.refresh_from_db()
        self.assertIsNone(tale.deleted_at)

    def test_update_deleted_using_model(self):
        tale = DarkTaleFactory(dark_level=666)
        tale.delete()

        tale.dark_level = 42
        with self.assertRaises(exceptions.UpdatingSoftDeletedException):
            tale.save()

        tale.refresh_from_db()
        self.assertNotEqual(42, tale.description)
        self.assertIsNotNone(tale.deleted_at)

    def test_update_deleted_using_queryset(self):
        tale_a = DarkTaleFactory(dark_level=666)
        tale_b = DarkTaleFactory(dark_level=666)
        tale_b.delete()

        DarkTale.objects.all().update(dark_level=42)

        tale_a.refresh_from_db()
        self.assertEqual(42, tale_a.dark_level)

        tale_b.refresh_from_db()
        self.assertNotEqual(42, tale_b.dark_level)

    def test_delete_using_model(self):
        tale = DarkTaleFactory()
        tale.delete()

        tale.refresh_from_db()
        self.assertIsNotNone(tale.deleted_at)

    def test_delete_using_queryset(self):
        tale_a = DarkTaleFactory()
        tale_b = DarkTaleFactory()

        DarkTale.objects.all().delete()

        tale_a.refresh_from_db()
        self.assertIsNotNone(tale_a.deleted_at)

        tale_b.refresh_from_db()
        self.assertIsNotNone(tale_b.deleted_at)

    def test_filter_by_default(self):
        tale_a = DarkTaleFactory()
        tale_b = DarkTaleFactory()
        tale_b.delete()
        tale_c = DarkTaleFactory()

        tales = DarkTale.objects.all()
        self.assertEqual(2, tales.count())

        [fetched_tale_a, fetched_tale_c] = tales
        self.assertEqual(tale_a, fetched_tale_a)
        self.assertEqual(tale_c, fetched_tale_c)

        tale_b.refresh_from_db()
        self.assertIsNotNone(tale_b.deleted_at)

    def test_filter_with_deleted(self):
        tale_a = DarkTaleFactory()
        tale_b = DarkTaleFactory()
        tale_b.delete()
        tale_c = DarkTaleFactory()

        tales = DarkTale.objects.all_with_deleted()
        self.assertEqual(3, tales.count())

        [fetched_tale_a, fetched_tale_c, fetched_tale_b] = tales
        self.assertEqual(tale_a, fetched_tale_a)
        self.assertEqual(tale_b, fetched_tale_b)
        self.assertEqual(tale_c, fetched_tale_c)

        tale_b.refresh_from_db()
        self.assertIsNotNone(tale_b.deleted_at)

    # INHERITANCE FEATURES
    def test_create_parent_model(self):
        tale = TaleFactory()
        self.assertEqual("tale", tale.type)

        self.assertFalse(EnvironmentalSpell.objects.exists())
        self.assertFalse(CombatSpell.objects.exists())

    def test_create_child_model(self):
        tale_a = DarkTaleFactory()
        self.assertEqual("darktale", tale_a.type)

        tale_b = HappyTaleFactory()
        self.assertEqual("happytale", tale_b.type)

        tales = Tale.objects.all()
        self.assertEqual(2, tales.count())
