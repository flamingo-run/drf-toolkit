from unittest.mock import ANY

from drf_kit.tests import BaseApiTest
from test_app.tests.tests_base import HogwartsTestMixin


class TestVeryCustomView(HogwartsTestMixin, BaseApiTest):
    url = '/wizards'

    def setUp(self):
        super().setUp()
        self.wizards = self._set_up_wizards()

    def test_list_endpoint(self):
        url = self.url

        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        data = response.json()
        self.assertEqual(4, len(data['results']))

        expected = list(reversed(self.expected_wizards))
        self.assertEqual(expected, data['results'])

    def test_detail_endpoint_out_of_queryset(self):
        # This endpoint detail queryset allows only age > 18
        wizard = self.wizards[0]
        url = f'{self.url}/{wizard.pk}'

        response = self.client.get(url)
        self.assertEqual(404, response.status_code)

    def test_detail_endpoint(self):
        wizard = self.wizards[3]
        url = f'{self.url}/{wizard.pk}'

        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        data = response.json()
        expected = self.expected_detailed_wizards[3]
        self.assertEqual(expected, data)

    def test_create_endpoint(self):
        url = self.url
        data = {
            'name': 'Luna Lovegood',
            'plz_ignore_me': 666,
        }
        response = self.client.post(url, data)
        self.assertEqual(201, response.status_code)

        data = response.json()
        expected = {
            'id': ANY,
            'name': 'Luna Lovegood',
            'age': None,
            'is_half_blood': False,
            'received_letter_at': None,
            'created_at': ANY,
            'updated_at': ANY,
            'picture': None,
            'house': None,
        }
        self.assertEqual(expected, data)

    def test_update_endpoint(self):
        wizard = self.wizards[0]
        url = f'{self.url}/{wizard.pk}'
        data = {
            'age': 99,
            'plz_ignore_me': 666,
        }
        response = self.client.patch(url, data)
        self.assertEqual(200, response.status_code)

        data = response.json()
        expected = self.expected_detailed_wizards[0]
        expected['age'] = 99
        self.assertEqual(expected, data)
