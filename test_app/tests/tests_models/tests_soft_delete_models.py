from drf_kit import exceptions
from drf_kit.tests import BaseApiTest
from test_app.models import Memory
from test_app.tests.factories.memory_factories import MemoryFactory
from test_app.tests.factories.wizard_factories import WizardFactory
from test_app.tests.tests_base import HogwartsTestMixin


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
