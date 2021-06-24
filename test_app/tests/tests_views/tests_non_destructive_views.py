from unittest.mock import ANY

from drf_kit.tests import BaseApiTest
from test_app import models
from test_app.tests.tests_base import HogwartsTestMixin


class TestNonDestructiveView(HogwartsTestMixin, BaseApiTest):
    url = "/wands"

    def setUp(self):
        super().setUp()
        self.wands = self._set_up_wands()

    def test_list_endpoint(self):
        url = self.url

        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        data = response.json()

        expected = [
            self.expected_wands[4],
            self.expected_wands[3],
            self.expected_wands[2],
            self.expected_wands[1],
            self.expected_wands[0],
        ]
        self.assertEqual(expected, data["results"])

    def test_detail_endpoint(self):
        wand = self.wands[0]
        url = f"{self.url}/{wand.pk}"

        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        data = response.json()
        self.assertEqual(self.expected_wands[0], data)

    def test_post_endpoint(self):
        url = self.url

        data = {
            "name": "Holly",
        }
        response = self.client.post(url, data=data)
        self.assertEqual(201, response.status_code)

        data = response.json()
        expected = {
            "id": ANY,
            "name": "Holly",
        }
        self.assertEqual(expected, data)

        wands = models.Wand.objects.all()

        expected_amount = len(self.wands) + 1
        self.assertEqual(expected_amount, wands.count())

    def test_patch_endpoint(self):
        wand = self.wands[0]
        url = f"{self.url}/{wand.pk}"
        data = {
            "name": "Hazel",
        }
        response = self.client.patch(url, data=data)
        self.assertEqual(200, response.status_code)

        expected_wand = self.expected_wands[0]
        expected_wand["name"] = "Hazel"
        self.assertEqual(expected_wand, response.json())

        wands = models.Wand.objects.all()
        expected_amount = len(self.wands)
        self.assertEqual(expected_amount, wands.count())

    def test_put_endpoint(self):
        wand = self.wands[0]
        url = f"{self.url}/{wand.pk}"
        data = {
            "name": "Holly",
        }
        response = self.client.put(url, data=data)
        self.assertEqual(405, response.status_code)

    def test_delete_endpoint(self):
        wand = self.wands[0]
        url = f"{self.url}/{wand.pk}"
        response = self.client.delete(url)
        self.assertEqual(405, response.status_code)

        wands = models.Wand.objects.all()
        expected_amount = len(self.wands)
        self.assertEqual(expected_amount, wands.count())
