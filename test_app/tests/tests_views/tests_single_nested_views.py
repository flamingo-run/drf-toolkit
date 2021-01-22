from unittest.mock import ANY

from drf_kit.tests import BaseApiTest
from test_app import models
from test_app.tests.tests_base import HogwartsTestMixin


class TestSingleNestView(HogwartsTestMixin, BaseApiTest):
    def setUp(self):
        super().setUp()
        self.wizards = self._set_up_wizards()
        self.patronus = self._set_up_patronus(wizards=self.wizards)

    def url(self, wizard_pk=None):
        return '/wizards/{id}/patronus'.format(id=wizard_pk or self.wizards[0].pk)

    def test_list_endpoint(self):
        url = self.url()

        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        data = response.json()
        self.assertEqual(
            self.expected_patronus[0],
            data,
        )

    def test_detail_endpoint(self):
        pk = self.patronus[0].pk
        url = f'{self.url()}/{pk}'

        response = self.client.get(url)
        self.assertEqual(405, response.status_code)

    def test_create_endpoint(self):
        wizard = self.wizards[2]
        url = self.url(wizard_pk=wizard.pk)

        data = {
            'name': 'Snake',
        }
        response = self.client.post(url, data)
        self.assertEqual(201, response.status_code)

        wizard.refresh_from_db()
        self.assertEqual('Snake', wizard.patronus.name)
        self.assertEqual(None, wizard.patronus.color)

        self.assertEqual(4, models.Patronus.objects.count())

    def test_create_endpoint_with_existing(self):
        wizard = self.wizards[0]
        url = self.url(wizard_pk=wizard.pk)

        data = {
            'name': 'Snake',
        }
        response = self.client.post(url, data)
        self.assertEqual(409, response.status_code)

        wizard.refresh_from_db()
        self.assertNotEqual('Snake', wizard.patronus.name)

        self.assertEqual(3, models.Patronus.objects.count())

    def test_put_endpoint(self):
        wizard = self.wizards[2]
        url = self.url(wizard_pk=wizard.pk)

        data = {
            'name': 'Snake',
        }
        response = self.client.put(url, data)
        self.assertEqual(405, response.status_code)

    def test_put_endpoint_with_existing(self):
        wizard = self.wizards[0]
        url = self.url(wizard_pk=wizard.pk)

        data = {
            'name': 'Snake',
        }
        response = self.client.put(url, data)
        self.assertEqual(405, response.status_code)

    def test_patch_endpoint(self):
        wizard = self.wizards[2]
        url = self.url(wizard_pk=wizard.pk)

        data = {
            'name': 'Snake',
        }
        response = self.client.patch(url, data)
        self.assertEqual(200, response.status_code)

        data = response.json()
        expected_data = {
            'id': ANY,
            'name': 'Snake',
            'color': None,
            'wizard': self.expected_wizards[2],
        }
        self.assertEqual(expected_data, data)

        wizard.refresh_from_db()
        self.assertEqual('Snake', wizard.patronus.name)
        self.assertEqual(None, wizard.patronus.color)

        self.assertEqual(4, models.Patronus.objects.count())

    def test_patch_endpoint_with_existing(self):
        wizard = self.wizards[0]
        url = self.url(wizard_pk=wizard.pk)

        data = {
            'name': 'White Stag',
        }
        response = self.client.patch(url, data)
        self.assertEqual(200, response.status_code)

        data = response.json()
        expected_data = {
            'id': ANY,
            'name': 'White Stag',
            'color': 'purple',
            'wizard': self.expected_wizards[0],
        }
        self.assertEqual(expected_data, data)

        wizard.refresh_from_db()
        self.assertEqual('White Stag', wizard.patronus.name)
        self.assertEqual('purple', wizard.patronus.color)

        self.assertEqual(3, models.Patronus.objects.count())

    def test_patch_endpoint_with_pk(self):
        pk = self.patronus[0].pk
        url = f'{self.url()}/{pk}'

        data = {
            'name': 'White Stag',
        }
        response = self.client.patch(url, data)
        self.assertEqual(405, response.status_code)

    def test_delete_endpoint(self):
        wizard = self.wizards[0]
        url = self.url(wizard_pk=wizard.pk)

        response = self.client.delete(url)
        self.assertEqual(204, response.status_code)

        wizard.refresh_from_db()
        with self.assertRaises(models.Patronus.DoesNotExist):
            _ = wizard.patronus

    def test_delete_endpoint_with_pk(self):
        wizard = self.wizards[0]
        patronus = self.patronus[0]
        url = f'{self.url(wizard_pk=wizard.pk)}/{patronus.pk}'

        response = self.client.delete(url)
        self.assertEqual(405, response.status_code)
