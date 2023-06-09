from unittest.mock import ANY

from rest_framework import status

from drf_kit.tests import BaseApiTest
from test_app import models
from test_app.tests.factories.tri_wizard_placement_factories import TriWizardPlacementFactory
from test_app.tests.tests_base import HogwartsTestMixin


class TestUpsertView(HogwartsTestMixin, BaseApiTest):
    url = "/tri-wizard-placements"

    def setUp(self):
        super().setUp()
        self._set_up_wizards()
        self._set_up_placements()

    def test_list_endpoint(self):
        url = self.url

        response = self.client.get(url)

        expected = list(self.expected_placements)
        self.assertResponseList(expected_items=expected, response=response)

    def test_detail_endpoint(self):
        house = self.placements[0]
        url = f"{self.url}/{house.pk}"

        response = self.client.get(url)

        expected = self.expected_placements[0]
        self.assertResponseDetail(expected_item=expected, response=response)

    def test_post_endpoint(self):
        wizard = self.wizards[0]

        url = self.url
        data = {
            "year": 2000,
            "wizard_id": wizard.pk,
            "prize": "wand",
        }
        response = self.client.post(url, data=data)

        expected = {
            "id": ANY,
            "year": 2000,
            "wizard_id": wizard.pk,
        }
        self.assertResponseCreate(expected_item=expected, response=response)

        placements = models.TriWizardPlacement.objects.all()
        self.assertEqual(5, placements.count())

    def test_post_endpoint_with_duplicate_unique_together(self):
        placement = self.placements[0]

        url = self.url
        data = {
            "wizard_id": placement.wizard.pk,
            "year": placement.year,
            "prize": "stone",
        }

        response = self.client.post(url, data=data)

        expected = {
            "id": ANY,
            "wizard_id": placement.wizard.pk,
            "year": placement.year,
        }
        self.assertResponseUpdated(expected_item=expected, response=response)

        placements = models.TriWizardPlacement.objects.all()
        self.assertEqual(4, placements.count())

    def test_post_endpoint_with_duplicate_unique(self):
        placement = self.placements[0]

        url = self.url
        data = {
            "year": 2000,
            "wizard_id": placement.wizard.pk,
            "prize": placement.prize,
        }

        response = self.client.post(url, data=data)

        expected = {
            "id": ANY,
            "wizard_id": placement.wizard.pk,
            "year": 2000,
        }
        self.assertResponseUpdated(expected_item=expected, response=response)

        placements = models.TriWizardPlacement.objects.all()
        self.assertEqual(4, placements.count())

    def test_post_with_one_duplicate_prize(self):
        placement = TriWizardPlacementFactory(prize="ball-red")
        TriWizardPlacementFactory.create_batch(3)  # noise

        url = self.url
        data = {
            "wizard_id": self.wizards[0].pk,
            "prize": "ball",
            "year": 2000,
        }

        response = self.client.post(url, data=data)

        expected = {
            "id": placement.pk,  # upserted
            "wizard_id": self.wizards[0].pk,  # updated
            "year": 2000,  # updated
        }
        self.assertResponseUpdated(expected_item=expected, response=response)

        placement.refresh_from_db()
        self.assertEqual(placement.prize, "ball")  # updated

    def test_post_with_many_duplicate_prize(self):
        placement_a = TriWizardPlacementFactory(prize="ball-red", year=1990)
        placement_b = TriWizardPlacementFactory(prize="ball-blue", year=1991)
        TriWizardPlacementFactory.create_batch(3)  # noise

        url = self.url
        data = {
            "wizard_id": self.wizards[0].pk,
            "prize": "ball",
            "year": 2000,
        }

        response = self.client.post(url, data=data)
        self.assertEqual(status.HTTP_409_CONFLICT, response.status_code)
        expected_error = {"errors": f"Model is duplicated with Placement {placement_a.pk} | Placement {placement_b.pk}"}
        self.assertEqual(expected_error, response.json())

    def test_patch_endpoint(self):
        placements = self.placements[0]
        url = f"{self.url}/{placements.pk}"
        data = {
            "year": 1951,
        }
        response = self.client.patch(url, data=data)

        expected_placement = self.expected_placements[0]
        expected_placement["year"] = 1951
        self.assertResponseUpdated(expected_item=expected_placement, response=response)

        placements = models.TriWizardPlacement.objects.all()
        self.assertEqual(4, placements.count())

    def test_put_endpoint(self):
        placement = self.placements[0]
        url = f"{self.url}/{placement.pk}"
        data = {
            "wizard_id": placement.wizard.pk,
            "year": 2000,
        }
        response = self.client.put(url, data=data)
        self.assertResponseNotAllowed(response=response)

    def test_delete_endpoint(self):
        placement = self.placements[0]
        url = f"{self.url}/{placement.pk}"
        response = self.client.delete(url)
        self.assertResponseDeleted(response=response)

        placements = models.TriWizardPlacement.objects.all()
        self.assertEqual(3, placements.count())
