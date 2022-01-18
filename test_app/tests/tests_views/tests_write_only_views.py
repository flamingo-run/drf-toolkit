from unittest.mock import ANY

from drf_kit.tests import BaseApiTest
from test_app import models
from test_app.tests.tests_base import HogwartsTestMixin


class TestWriteOnlyView(HogwartsTestMixin, BaseApiTest):
    url = "/memories"

    def setUp(self):
        super().setUp()
        self._set_up_wizards()
        self._set_up_memories()

    def test_list_endpoint(self):
        url = self.url

        response = self.client.get(url)
        self.assertResponseNotAllowed(response=response)

    def test_detail_endpoint(self):
        memory = self.memories[0]
        url = f"{self.url}/{memory.pk}"

        response = self.client.get(url)
        self.assertResponseNotAllowed(response=response)

    def test_post_endpoint(self):
        url = self.url

        wizard = self.wizards[0]
        data = {
            "owner_id": wizard.pk,
            "description": "Dad dead",
        }
        response = self.client.post(url, data=data)

        expected = {
            "id": ANY,
            "description": "Dad dead",
            "owner_id": wizard.pk,
        }
        self.assertResponseCreate(expected_item=expected, response=response)

        memories = models.Memory.objects.all()
        self.assertEqual(4, memories.count())

    def test_patch_endpoint(self):
        memory = self.memories[0]
        url = f"{self.url}/{memory.pk}"
        data = {
            "description": "Under the stairs",
        }
        response = self.client.patch(url, data=data)

        expected_memory = self.expected_memories[0]
        expected_memory["description"] = "Under the stairs"
        self.assertResponseUpdated(expected_item=expected_memory, response=response)

        memories = models.Memory.objects.all()
        self.assertEqual(3, memories.count())

    def test_put_endpoint(self):
        memory = self.memories[0]
        url = f"{self.url}/{memory.pk}"
        data = {
            "description": "Under the stairs",
        }
        response = self.client.put(url, data=data)
        self.assertResponseNotAllowed(response=response)

    def test_delete_endpoint(self):
        memory = self.memories[0]
        url = f"{self.url}/{memory.pk}"
        response = self.client.delete(url)
        self.assertResponseDeleted(response=response)

        memories = models.Memory.objects.all()
        self.assertEqual(2, memories.count())
