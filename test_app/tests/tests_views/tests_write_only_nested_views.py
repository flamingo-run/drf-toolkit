from unittest.mock import ANY

from rest_framework import status

from drf_kit.tests import BaseApiTest
from test_app.models import Memory
from test_app.tests.tests_base import HogwartsTestMixin


class TestWriteOnlyNestedView(HogwartsTestMixin, BaseApiTest):
    def setUp(self):
        super().setUp()
        self._set_up_wizards()
        self._set_up_memories()

    @property
    def url(self):
        return f"/wizards/{self.wizards[0].pk}/memories"

    def test_list_endpoint(self):
        url = self.url

        response = self.client.get(url)
        self.assertResponseNotAllowed(response=response)

    def test_detail_endpoint(self):
        pk = self.memories[0].pk
        url = f"{self.url}/{pk}"

        response = self.client.get(url)
        self.assertResponseNotAllowed(response=response)

    def test_create_endpoint(self):
        url = self.url

        wizard = self.wizards[0]
        data = {
            "description": "Old man falls",
        }
        response = self.client.post(url, data)

        expected_data = {
            "id": ANY,
            "description": "Old man falls",
            "owner_id": wizard.pk,
        }
        self.assertResponseCreate(expected_item=expected_data, response=response)

    def test_create_endpoint_unnecessary_pk(self):
        url = self.url
        wizard = self.wizards[0]
        data = {
            "description": "Old man falls",
            "owner_id": wizard.pk,
        }
        response = self.client.post(url, data)

        expected_data = {
            "id": ANY,
            "description": "Old man falls",
            "owner_id": wizard.pk,
        }
        self.assertResponseCreate(expected_item=expected_data, response=response)

    def test_create_endpoint_another_nest(self):
        url = self.url

        wizard = self.wizards[3]
        data = {
            "owner_id": wizard.pk,
            "description": "Old man falls",
        }
        response = self.client.post(url, data)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_patch_endpoint(self):
        pk = self.memories[0].pk
        url = f"{self.url}/{pk}"

        data = {
            "description": "Old man falls",
        }
        response = self.client.patch(url, data)

        expected_data = self.expected_memories[0]
        expected_data["description"] = "Old man falls"
        self.assertResponseUpdated(expected_item=expected_data, response=response)

    def test_delete_endpoint(self):
        pk = self.memories[0].pk
        url = f"{self.url}/{pk}"

        response = self.client.delete(url)
        self.assertResponseDeleted(response=response)

        self.assertTrue(Memory.objects.get(pk=pk).is_deleted)

    def test_action_on_item_from_another_nest(self):
        pk = self.memories[2].pk
        url = f"{self.url}/{pk}"

        data = {
            "description": "weird dreams",
        }

        response = self.client.patch(url, data=data)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

        response = self.client.patch(url, data={"age": 99})
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

        response = self.client.delete(url)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
