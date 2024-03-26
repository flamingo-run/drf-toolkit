from unittest.mock import ANY

from rest_framework import status

from drf_kit.tests import BaseApiTest
from test_app import models
from test_app.tests.tests_base import HogwartsTestMixin


class TestManyToManyView(HogwartsTestMixin, BaseApiTest):
    url = "/spell-casts"

    def setUp(self):
        super().setUp()
        self._set_up_wizards()
        self._set_up_spells()
        self._set_up_spell_casts()

    def test_list_endpoint(self):
        url = self.url

        response = self.client.get(url)

        expected = list(reversed(self.expected_spell_casts))
        self.assertResponseList(expected_items=expected, response=response)

    def test_detail_endpoint(self):
        spell_cast = self.spell_casts[0]
        url = f"{self.url}/{spell_cast.pk}"

        response = self.client.get(url)

        expected = self.expected_spell_casts[0]
        self.assertResponseDetail(expected_item=expected, response=response)

    def test_post_endpoint(self):
        wizard = self.wizards[3]
        spell = self.spells[0]

        url = self.url
        data = {
            "wizard_id": wizard.pk,
            "spell_id": spell.pk,
            "is_successful": False,
        }
        response = self.client.post(url, data=data)

        expected = {
            "id": ANY,
            "wizard": self.expected_detailed_wizards[3],
            "spell": self.expected_spells[0],
            "is_successful": False,
        }
        self.assertResponseCreate(expected_item=expected, response=response)

        spell_casts = models.SpellCast.objects.all()
        self.assertEqual(5, spell_casts.count())

    def test_post_endpoint_with_fk_not_found(self):
        wizard = self.wizards[3]

        url = self.url
        data = {
            "wizard_id": wizard.pk,
            "spell_id": 666,
            "is_successful": False,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

        data = response.json()

        self.assertIn("spell_id", data)
        self.assertIn("object does not exist", data["spell_id"][0])

        spell_casts = models.SpellCast.objects.all()
        self.assertEqual(4, spell_casts.count())

    def test_patch_endpoint(self):
        spell_cast = self.spell_casts[0]
        url = f"{self.url}/{spell_cast.pk}"
        data = {
            "is_successful": True,
        }
        response = self.client.patch(url, data=data)

        expected_spell_cast = self.expected_spell_casts[0]
        expected_spell_cast["is_successful"] = True
        self.assertResponseUpdated(expected_item=expected_spell_cast, response=response)

        spell_casts = models.SpellCast.objects.all()
        self.assertEqual(4, spell_casts.count())

    def test_put_endpoint(self):
        spell_cast = self.spell_casts[0]
        url = f"{self.url}/{spell_cast.pk}"
        data = {
            "wizard_id": self.wizards[3].pk,
            "spell_id": self.spells[0].pk,
            "is_successful": False,
        }
        response = self.client.put(url, data=data)
        self.assertResponseNotAllowed(response=response)

    def test_delete_endpoint(self):
        spell_cast = self.spell_casts[0]
        url = f"{self.url}/{spell_cast.pk}"
        response = self.client.delete(url)
        self.assertResponseDeleted(response=response)

        with self.assertRaises(models.SpellCast.DoesNotExist):
            spell_cast.refresh_from_db()
