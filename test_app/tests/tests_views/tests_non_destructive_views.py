from unittest.mock import ANY

from drf_kit.tests import BaseApiTest
from test_app import models
from test_app.tests.tests_base import HogwartsTestMixin


class TestNonDestructiveView(HogwartsTestMixin, BaseApiTest):
    url = "/wands"

    def setUp(self):
        super().setUp()
        self._set_up_wands()

    def test_list_endpoint(self):
        url = self.url

        response = self.client.get(url)

        expected = [
            self.expected_wands[4],
            self.expected_wands[3],
            self.expected_wands[2],
            self.expected_wands[1],
            self.expected_wands[0],
        ]
        self.assertResponseList(expected_items=expected, response=response)

    def test_detail_endpoint(self):
        wand = self.wands[0]
        url = f"{self.url}/{wand.pk}"

        response = self.client.get(url)

        expected = self.expected_wands[0]
        self.assertResponseDetail(expected_item=expected, response=response)

    def test_post_endpoint(self):
        url = self.url

        data = {
            "name": "Holly",
        }
        response = self.client.post(url, data=data)

        expected = {
            "id": ANY,
            "name": "Holly",
        }
        self.assertResponseCreate(expected_item=expected, response=response)

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

        expected_wand = self.expected_wands[0]
        expected_wand["name"] = "Hazel"
        self.assertResponseUpdated(expected_item=expected_wand, response=response)

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
        self.assertResponseNotAllowed(response=response)

    def test_delete_endpoint(self):
        wand = self.wands[0]
        url = f"{self.url}/{wand.pk}"
        response = self.client.delete(url)
        self.assertResponseNotAllowed(response=response)

        wands = models.Wand.objects.all()
        expected_amount = len(self.wands)
        self.assertEqual(expected_amount, wands.count())
