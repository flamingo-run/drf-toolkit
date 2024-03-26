from drf_kit import exceptions
from drf_kit.tests import BaseApiTest
from test_app.models import CombatSpell, DarkTale, EnvironmentalSpell, Tale
from test_app.tests.factories.tale_factories import DarkTaleFactory, HappyTaleFactory, TaleFactory
from test_app.tests.tests_base import HogwartsTestMixin


class TestSoftDeleteInheritanceOrderedModel(HogwartsTestMixin, BaseApiTest):
    # ORDERING FEATURES
    def assertOrder(self, obj, expected_order):
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
