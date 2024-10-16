from drf_kit.tests import BaseApiTest
from test_app.tests.factories.spell_factories import SpellFactory


class TestPaginatedView(BaseApiTest):
    url = "/spells"

    def setUp(self):
        super().setUp()
        self.spells = [SpellFactory(id=i, name=str(i).zfill(3)) for i in range(1, 50)]

    def test_first_page(self):
        url = self.url

        response = self.client.get(url, {"page_size": 12})

        self.assertEqual(list(range(1, 13)), [spell["id"] for spell in response.json()["results"]])
        self.assertRegex(response.json()["next"], r"page=2")
        self.assertEqual(None, response.json()["previous"])
        self.assertEqual(len(self.spells), response.json()["count"])

    def test_second_page(self):
        url = self.url

        response = self.client.get(url, {"page_size": 12, "page": 2})

        self.assertEqual(list(range(13, 25)), [spell["id"] for spell in response.json()["results"]])
        self.assertRegex(response.json()["next"], r"page=3")
        self.assertNotRegex(response.json()["previous"], r"page=\d+")
        self.assertEqual(len(self.spells), response.json()["count"])

    def test_third_page(self):
        url = self.url

        response = self.client.get(url, {"page_size": 12, "page": 3})

        self.assertEqual(list(range(25, 37)), [spell["id"] for spell in response.json()["results"]])
        self.assertRegex(response.json()["next"], r"page=4")
        self.assertRegex(response.json()["previous"], r"page=2")
        self.assertEqual(len(self.spells), response.json()["count"])

    def test_fourth_page(self):
        url = self.url

        response = self.client.get(url, {"page_size": 12, "page": 4})

        self.assertEqual(list(range(37, 49)), [spell["id"] for spell in response.json()["results"]])
        self.assertRegex(response.json()["next"], r"page=5")
        self.assertRegex(response.json()["previous"], r"page=3")
        self.assertEqual(len(self.spells), response.json()["count"])

    def test_last_page(self):
        url = self.url

        response = self.client.get(url, {"page_size": 12, "page": 5})

        self.assertEqual(list(range(49, 50)), [spell["id"] for spell in response.json()["results"]])
        self.assertEqual(None, response.json().get("next"))
        self.assertRegex(response.json()["previous"], r"page=4")
        self.assertEqual(len(self.spells), response.json()["count"])

    def test_invalid_page(self):
        url = self.url

        response = self.client.get(url, {"page_size": 12, "page": 15000})
        self.assertResponseNotFound(response=response, expected_item={"detail": "Invalid page."})


class TestLightPaginatedView(TestPaginatedView):
    url = "/spells-light"

    def test_first_page(self):
        url = self.url

        response = self.client.get(url, {"page_size": 12})

        self.assertEqual(list(range(1, 13)), [spell["id"] for spell in response.json()["results"]])
        self.assertRegex(response.json()["next"], r"page=2")
        self.assertEqual(None, response.json()["previous"])
        self.assertNotIn("count", response.json())

    def test_second_page(self):
        url = self.url

        response = self.client.get(url, {"page_size": 12, "page": 2})

        self.assertEqual(list(range(13, 25)), [spell["id"] for spell in response.json()["results"]])
        self.assertRegex(response.json()["next"], r"page=3")
        self.assertNotRegex(response.json()["previous"], r"page=\d+")
        self.assertNotIn("count", response.json())

    def test_third_page(self):
        url = self.url

        response = self.client.get(url, {"page_size": 12, "page": 3})

        self.assertEqual(list(range(25, 37)), [spell["id"] for spell in response.json()["results"]])
        self.assertRegex(response.json()["next"], r"page=4")
        self.assertRegex(response.json()["previous"], r"page=2")
        self.assertNotIn("count", response.json())

    def test_fourth_page(self):
        url = self.url

        response = self.client.get(url, {"page_size": 12, "page": 4})

        self.assertEqual(list(range(37, 49)), [spell["id"] for spell in response.json()["results"]])
        self.assertRegex(response.json()["next"], r"page=5")
        self.assertRegex(response.json()["previous"], r"page=3")
        self.assertNotIn("count", response.json())

    def test_last_page(self):
        url = self.url

        response = self.client.get(url, {"page_size": 12, "page": 5})

        self.assertEqual(list(range(49, 50)), [spell["id"] for spell in response.json()["results"]])
        self.assertEqual(None, response.json().get("next"))
        self.assertRegex(response.json()["previous"], r"page=4")
        self.assertNotIn("count", response.json())

    def test_invalid_page(self):
        url = self.url

        response = self.client.get(url, {"page_size": 12, "page": 15000})
        self.assertEqual([], response.json()["results"])
        self.assertEqual(None, response.json().get("next"))
        self.assertRegex(response.json()["previous"], r"page=14999")
        self.assertNotIn("count", response.json())
