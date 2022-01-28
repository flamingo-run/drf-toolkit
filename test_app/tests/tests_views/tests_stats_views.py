from rest_framework import status

from drf_kit.tests import BaseApiTest
from test_app.tests.tests_base import HogwartsTestMixin


class TestStatsView(HogwartsTestMixin, BaseApiTest):
    url = "/houses"

    def setUp(self):
        super().setUp()
        self._set_up_houses()
        self._set_up_wizards()
        self._set_up_wizard_houses()

    def test_list_endpoint(self):
        url = f"{self.url}?stats=1"

        response = self.client.get(url)

        # sorted by name ASC
        expected = [
            self.expected_stats_houses[0],
            self.expected_stats_houses[3],
            self.expected_stats_houses[2],
            self.expected_stats_houses[1],
        ]
        self.assertResponseList(expected, response)

    def test_detail_endpoint(self):
        house = self.houses[0]
        url = f"{self.url}/{house.pk}?stats=1"

        response = self.client.get(url)
        self.assertResponseDetail(self.expected_stats_houses[0], response)

    def test_list_endpoint_wrong_parameter(self):
        house = self.houses[0]
        url = f"{self.url}/{house.pk}?stats=potato"

        response = self.client.get(url)

        expected_error = {"stats": "Stats parameter must be an integer"}
        self.assertResponse(
            expected_status=status.HTTP_400_BAD_REQUEST,
            expected_body=expected_error,
            response=response,
        )
