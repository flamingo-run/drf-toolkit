from drf_kit.tests import BaseApiTest
from test_app import models
from test_app.tests.tests_base import HogwartsTestMixin


class TestReadOnlyView(HogwartsTestMixin, BaseApiTest):
    url = "/spells"

    def setUp(self):
        super().setUp()
        self._set_up_spells()

    def test_list_endpoint(self):
        url = self.url

        response = self.client.get(url)

        expected = [
            self.expected_spells[0],
            self.expected_spells[2],
            self.expected_spells[1],
        ]
        self.assertResponseList(expected_items=expected, response=response)

    def test_detail_endpoint(self):
        spell = self.spells[0]
        url = f"{self.url}/{spell.pk}"

        response = self.client.get(url)

        expected = self.expected_spells[0]
        self.assertResponseDetail(expected_item=expected, response=response)

    def test_post_endpoint(self):
        url = self.url
        data = {
            "name": "Leviosa",
        }
        response = self.client.post(url, data=data)
        self.assertResponseNotAllowed(response=response)

        spells = models.Spell.objects.all()
        self.assertEqual(3, spells.count())

    def test_patch_endpoint(self):
        spell = self.spells[0]
        url = f"{self.url}/{spell.pk}"
        data = {
            "name": "Leviosa",
        }
        response = self.client.patch(url, data=data)
        self.assertResponseNotAllowed(response=response)

        spell.refresh_from_db()
        self.assertNotEqual("Leviosa", spell.name)

    def test_put_endpoint(self):
        url = f"{self.url}/42"
        data = {
            "name": "Leviosa",
        }
        response = self.client.put(url, data=data)
        self.assertResponseNotAllowed(response=response)

    def test_delete_endpoint(self):
        spell = self.spells[0]
        url = f"{self.url}/{spell.pk}"
        response = self.client.delete(url)
        self.assertResponseNotAllowed(response=response)

        spells = models.Spell.objects.all()
        self.assertEqual(3, spells.count())
