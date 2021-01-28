from unittest.mock import ANY, patch

from django.db import IntegrityError

from drf_kit.tests import BaseApiTest
from test_app import models
from test_app.tests.tests_base import HogwartsTestMixin


class TestCRUDView(HogwartsTestMixin, BaseApiTest):
    url = '/houses'

    def setUp(self):
        super().setUp()
        self.houses = self._set_up_houses()

    def test_list_endpoint(self):
        url = self.url

        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        data = response.json()

        expected = list(reversed(self.expected_houses))
        self.assertEqual(expected, data['results'])

    def test_detail_endpoint(self):
        house = self.houses[0]
        url = f'{self.url}/{house.pk}'

        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        data = response.json()
        self.assertEqual(self.expected_houses[0], data)

    def test_post_endpoint(self):
        url = self.url
        data = {
            'name': "#Always",
            'points_boost': 3.1,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(201, response.status_code)

        data = response.json()
        expected = {
            'id': ANY,
            'name': "#Always",
            'points_boost': "3.10",
            'created_at': ANY,
        }
        self.assertEqual(expected, data)

        houses = models.House.objects.all()
        self.assertEqual(5, houses.count())

    def test_post_endpoint_with_existing(self):
        url = self.url
        data = {
            'name': "Gryffindor",
            'points_boost': 66.6,
        }

        # IntegrityError by duplicate key is a very rare exception because the serializer
        # validators pre-check before committing them to the database
        # Then we have to simulate this error happening
        klass_name = 'drf_kit.serializers.BaseModelSerializer.create'
        error = IntegrityError(
            'duplicate key value violates unique constraint potato\n'
            'DETAIL:  Key (id)=(42) already exists.'
        )
        with patch(klass_name, side_effect=error):
            response = self.client.post(url, data=data)

        self.assertEqual(400, response.status_code)

        houses = models.House.objects.all()
        self.assertEqual(4, houses.count())

    def test_patch_endpoint(self):
        house = self.houses[0]
        url = f'{self.url}/{house.pk}'
        data = {
            'points_boost': 3.14,
        }
        response = self.client.patch(url, data=data)
        self.assertEqual(200, response.status_code)

        expected_house = self.expected_houses[0]
        expected_house['points_boost'] = "3.14"
        self.assertEqual(expected_house, response.json())

        houses = models.House.objects.all()
        self.assertEqual(4, houses.count())

    def test_put_endpoint(self):
        house = self.houses[0]
        url = f'{self.url}/{house.pk}'
        data = {
            'name': "Not Griffindor",
        }
        response = self.client.put(url, data=data)
        self.assertEqual(405, response.status_code)

    def test_delete_endpoint(self):
        house = self.houses[0]
        url = f'{self.url}/{house.pk}'
        response = self.client.delete(url)
        self.assertEqual(204, response.status_code)

        houses = models.House.objects.all()
        self.assertEqual(3, houses.count())
