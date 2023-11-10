from unittest.mock import ANY

from rest_framework import status

from drf_kit.tests import BaseApiTest
from test_app.tests.tests_base import HogwartsTestMixin


class TestVeryCustomView(HogwartsTestMixin, BaseApiTest):
    url = "/wizards"

    def setUp(self):
        super().setUp()
        self._set_up_wizards()

    def test_list_endpoint(self):
        url = self.url

        response = self.client.get(url)

        expected = list(reversed(self.expected_wizards))
        self.assertResponseList(expected_items=expected, response=response)

    def test_detail_endpoint_out_of_queryset(self):
        # This endpoint detail queryset allows only age > 18
        wizard = self.wizards[0]
        url = f"{self.url}/{wizard.pk}"

        response = self.client.get(url)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_detail_endpoint(self):
        wizard = self.wizards[3]
        url = f"{self.url}/{wizard.pk}"

        response = self.client.get(url)

        expected = self.expected_detailed_wizards[3]
        self.assertResponseDetail(expected_item=expected, response=response)

    def test_create_endpoint(self):
        url = self.url
        data = {
            "name": "Luna Lovegood",
            "plz_ignore_me": 666,
        }
        response = self.client.post(url, data)

        expected = {
            "id": ANY,
            "name": "Luna Lovegood",
            "age": None,
            "is_half_blood": False,
            "received_letter_at": None,
            "created_at": ANY,
            "updated_at": ANY,
            "picture": None,
            "house": None,
        }
        self.assertResponseCreate(expected_item=expected, response=response)

    def test_update(self):
        wizard = self.wizards[0]

        url = f"{self.url}/{wizard.id}"
        response = self.client.patch(url)
        self.assertResponseAccepted(response=response)

    def test_destroy(self):
        wizard = self.wizards[0]

        url = f"{self.url}/{wizard.id}"
        response = self.client.delete(url)
        self.assertResponseAccepted(response=response, expected_item="enqueue to be deleted")
