from unittest.mock import ANY

from drf_kit.tests import BaseApiTest
from test_app import models
from test_app.tests.tests_base import HogwartsTestMixin


class TestUpsertView(HogwartsTestMixin, BaseApiTest):
    url = '/tri-wizard-placements'

    def setUp(self):
        super().setUp()
        self.wizards = self._set_up_wizards()
        self.placements = self._set_up_placements(wizards=self.wizards)

    def test_list_endpoint(self):
        url = self.url

        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        data = response.json()

        expected = list(self.expected_placements)
        self.assertEqual(expected, data['results'])

    def test_detail_endpoint(self):
        house = self.placements[0]
        url = f'{self.url}/{house.pk}'

        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        data = response.json()
        self.assertEqual(self.expected_placements[0], data)

    def test_post_endpoint(self):
        wizard = self.wizards[0]

        url = self.url
        data = {
            'year': 2000,
            'wizard_id': wizard.pk,
            'prize': 'wand',
        }
        response = self.client.post(url, data=data)
        self.assertEqual(201, response.status_code)

        data = response.json()
        expected = {
            'id': ANY,
            'year': 2000,
            'wizard_id': wizard.pk,
        }
        self.assertEqual(expected, data)

        placements = models.TriWizardPlacement.objects.all()
        self.assertEqual(5, placements.count())

    def test_post_endpoint_with_duplicate_unique_together(self):
        placement = self.placements[0]

        url = self.url
        data = {
            'wizard_id': placement.wizard.pk,
            'year': placement.year,
            'prize': 'stone',
        }

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        placements = models.TriWizardPlacement.objects.all()
        self.assertEqual(4, placements.count())

    def test_post_endpoint_with_duplicate_unique(self):
        placement = self.placements[0]

        url = self.url
        data = {
            'year': 2000,
            'wizard_id': placement.wizard.pk,
            'prize': placement.prize,
        }

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        placements = models.TriWizardPlacement.objects.all()
        self.assertEqual(4, placements.count())

    def test_patch_endpoint(self):
        placements = self.placements[0]
        url = f'{self.url}/{placements.pk}'
        data = {
            'year': 1951,
        }
        response = self.client.patch(url, data=data)
        self.assertEqual(200, response.status_code)

        expected_placement = self.expected_placements[0]
        expected_placement['year'] = 1951
        self.assertEqual(expected_placement, response.json())

        placements = models.TriWizardPlacement.objects.all()
        self.assertEqual(4, placements.count())

    def test_put_endpoint(self):
        placement = self.placements[0]
        url = f'{self.url}/{placement.pk}'
        data = {
            'wizard_id': placement.wizard.pk,
            'year': 2000,
        }
        response = self.client.put(url, data=data)
        self.assertEqual(405, response.status_code)

    def test_delete_endpoint(self):
        placement = self.placements[0]
        url = f'{self.url}/{placement.pk}'
        response = self.client.delete(url)
        self.assertEqual(204, response.status_code)

        placements = models.TriWizardPlacement.objects.all()
        self.assertEqual(3, placements.count())
