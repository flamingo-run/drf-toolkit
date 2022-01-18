from unittest.mock import ANY

from drf_kit.tests import BaseApiTest
from test_app import models
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
