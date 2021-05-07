from unittest.mock import ANY

from drf_kit.tests import BaseApiTest
from test_app.models import Wizard
from test_app.tests.tests_base import HogwartsTestMixin


class TestNestedView(HogwartsTestMixin, BaseApiTest):
    def setUp(self):
        super().setUp()
        self.wizards = self._set_up_wizards()
        self.houses = self._set_up_houses()
        self._set_up_wizard_houses(wizards=self.wizards, houses=self.houses)

    @property
    def url(self):
        return "/houses/{id}/wizards".format(id=self.houses[0].pk)

    def test_list_endpoint(self):
        url = self.url

        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        data = response.json()
        self.assertEqual(2, len(data["results"]))

        expected_data = [
            self.expected_wizards[1],
            self.expected_wizards[0],
        ]

        self.assertEqual(expected_data, data["results"])

    def test_detail_endpoint(self):
        pk = self.wizards[0].pk
        url = f"{self.url}/{pk}"

        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        data = response.json()
        expected_data = self.expected_detailed_wizards[0]
        expected_data["house"] = self.expected_houses[0]
        self.assertEqual(expected_data, data)

    def test_create_endpoint(self):
        url = self.url

        data = {
            "name": "Luna Lovegood",
            "is_half_blood": False,
        }
        response = self.client.post(url, data)
        self.assertEqual(201, response.status_code)

        data = response.json()
        expected_data = {
            "id": ANY,
            "name": "Luna Lovegood",
            "age": None,
            "is_half_blood": False,
            "received_letter_at": None,
            "picture": None,
            "house": self.expected_houses[0],
            "created_at": ANY,
            "updated_at": ANY,
        }
        self.assertEqual(expected_data, data)

    def test_create_endpoint_unnecessary_pk(self):
        url = self.url

        data = {
            "name": "Luna Lovegood",
            "is_half_blood": False,
            "house_id": self.houses[0].pk,
        }
        response = self.client.post(url, data)
        self.assertEqual(201, response.status_code)

        data = response.json()
        expected_data = {
            "id": ANY,
            "name": "Luna Lovegood",
            "age": None,
            "is_half_blood": False,
            "received_letter_at": None,
            "picture": None,
            "house": self.expected_houses[0],
            "created_at": ANY,
            "updated_at": ANY,
        }
        self.assertEqual(expected_data, data)

    def test_create_endpoint_another_nest(self):
        url = self.url

        house = self.houses[3]
        data = {
            "name": "Luna Lovegood",
            "is_half_blood": False,
            "house_id": house.pk,
        }
        response = self.client.post(url, data)
        self.assertEqual(400, response.status_code)

    def test_patch_endpoint(self):
        pk = self.wizards[0].pk
        url = f"{self.url}/{pk}"

        data = {
            "age": 99,
        }
        response = self.client.patch(url, data)
        self.assertEqual(200, response.status_code)

        data = response.json()
        expected_data = self.expected_detailed_wizards[0]
        expected_data["age"] = 99
        expected_data["house"] = self.expected_houses[0]
        self.assertEqual(expected_data, data)

    def test_delete_endpoint(self):
        pk = self.wizards[1].pk
        url = f"{self.url}/{pk}"

        response = self.client.delete(url)
        self.assertEqual(204, response.status_code)
        self.assertFalse(Wizard.objects.filter(pk=pk).exists())

    def test_action_on_item_from_another_nest(self):
        pk = self.wizards[3].pk
        url = f"{self.url}/{pk}"

        response = self.client.get(url)
        self.assertEqual(404, response.status_code)

        response = self.client.patch(url, data={"age": 99})
        self.assertEqual(404, response.status_code)

        response = self.client.delete(url)
        self.assertEqual(404, response.status_code)
