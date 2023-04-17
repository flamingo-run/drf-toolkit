from unittest.mock import ANY

from test_app import models
from test_app.tests.tests_views.tests_crud_views import TestCRUDView


class TestBulkView(TestCRUDView):
    url = "/houses-bulk"

    def test_post_endpoint(self):
        url = self.url
        data = [
            {
                "name": "#Always",
                "points_boost": 3.1,
            },
            {
                "name": "#Never",
                "points_boost": 6.66,
            },
        ]
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(201, response.status_code)

        data = response.json()
        expected = [
            {
                "id": ANY,
                "name": "#Always",
                "points_boost": "3.10",
                "created_at": ANY,
            },
            {
                "id": ANY,
                "name": "#Never",
                "points_boost": "6.66",
                "created_at": ANY,
            },
        ]
        self.assertEqual(expected, data)

        houses = models.House.objects.all()
        self.assertEqual(6, houses.count())

    def test_patch_endpoint(self):
        house = self.houses[0]
        url = f"{self.url}/{house.pk}"
        data = {
            "points_boost": 3.14,
        }
        response = self.client.patch(url, data=data)
        self.assertEqual(405, response.status_code)

    def test_put_endpoint(self):
        house = self.houses[0]
        url = f"{self.url}/{house.pk}"
        data = {
            "name": "Not Griffindor",
        }
        response = self.client.put(url, data=data)
        self.assertEqual(405, response.status_code)

    def test_delete_endpoint(self):
        house = self.houses[0]
        url = f"{self.url}/{house.pk}"
        response = self.client.delete(url)
        self.assertEqual(204, response.status_code)

        houses = models.House.objects.all()
        self.assertEqual(3, houses.count())
