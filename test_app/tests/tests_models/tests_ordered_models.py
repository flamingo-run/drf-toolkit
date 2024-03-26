from drf_kit.tests import BaseApiTest
from test_app.tests.factories.tri_wizard_placement_factories import TriWizardPlacementFactory
from test_app.tests.tests_base import HogwartsTestMixin


class TestOrderedModel(HogwartsTestMixin, BaseApiTest):
    def setUp(self):
        super().setUp()
        self._set_up_wizards()

    def assertOrder(self, placement, expected_order):
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
