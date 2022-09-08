from unittest.mock import ANY, patch

from django.db import IntegrityError
from rest_framework import status

from drf_kit.tests import BaseApiTest
from test_app import models
from test_app.tests.tests_base import HogwartsTestMixin


class TestCRUDView(HogwartsTestMixin, BaseApiTest):
    url = "/houses"

    def setUp(self):
        super().setUp()
        self._set_up_houses()

    def _simulate_integrity_error(self, constraint="(id)=(42)"):
        # IntegrityError by duplicate key is a very rare exception because the serializer
        # validators pre-check before committing them to the database
        # Then we have to simulate this error happening
        klass_name = "django.db.models.Model.save"
        error = IntegrityError(
            "duplicate key value violates unique constraint potato\n" f"DETAIL:  Key {constraint} already exists."
        )
        return patch(klass_name, side_effect=error)

    def test_list_endpoint(self):
        url = self.url

        response = self.client.get(url)

        # sorted by name ASC
        expected = [
            self.expected_houses[0],
            self.expected_houses[3],
            self.expected_houses[2],
            self.expected_houses[1],
        ]
        self.assertResponseList(expected, response)

    def test_detail_endpoint(self):
        house = self.houses[0]
        url = f"{self.url}/{house.pk}"

        response = self.client.get(url)

        expected = self.expected_houses[0]
        self.assertResponseDetail(expected, response)

    def test_post_endpoint(self):
        url = self.url
        data = {
            "name": "#Always",
            "points_boost": 3.1,
        }
        response = self.client.post(url, data=data)

        expected = {
            "id": ANY,
            "name": "#Always",
            "points_boost": "3.10",
            "created_at": ANY,
        }
        self.assertResponseCreate(expected, response)

        houses = models.House.objects.all()
        self.assertEqual(5, houses.count())

    def test_post_endpoint_with_existing(self):
        url = self.url
        data = {
            "name": "Gryffindor",
            "points_boost": 66.6,
        }

        with self._simulate_integrity_error():
            response = self.client.post(url, data=data)

        self.assertEqual(409, response.status_code)
        expected = {"errors": "A House with `id=42` already exists."}
        self.assertResponse(expected_status=status.HTTP_409_CONFLICT, expected_body=expected, response=response)

        houses = models.House.objects.all()
        self.assertEqual(4, houses.count())

    def test_patch_endpoint(self):
        house = self.houses[0]
        url = f"{self.url}/{house.pk}"
        data = {
            "points_boost": 3.14,
        }
        response = self.client.patch(url, data=data)

        expected_house = self.expected_houses[0]
        expected_house["points_boost"] = "3.14"

        self.assertResponseUpdated(expected_item=expected_house, response=response)

        houses = models.House.objects.all()
        self.assertEqual(4, houses.count())

    def test_patch_endpoint_with_existing(self):
        house = self.houses[0]
        url = f"{self.url}/{house.pk}"
        data = {
            "points_boost": 3.14,
        }

        with self._simulate_integrity_error():
            response = self.client.patch(url, data=data)

        self.assertEqual(409, response.status_code)
        expected = {"errors": "A House with `id=42` already exists."}
        self.assertResponse(expected_status=status.HTTP_409_CONFLICT, expected_body=expected, response=response)

        houses = models.House.objects.all()
        self.assertEqual(4, houses.count())

    def test_put_endpoint(self):
        house = self.houses[0]
        url = f"{self.url}/{house.pk}"
        data = {
            "name": "Not Griffindor",
        }
        response = self.client.put(url, data=data)
        self.assertResponseNotAllowed(response=response)

    def test_delete_endpoint(self):
        house = self.houses[0]
        url = f"{self.url}/{house.pk}"
        response = self.client.delete(url)

        self.assertResponseDeleted(response=response)

        houses = models.House.objects.all()
        self.assertEqual(3, houses.count())
