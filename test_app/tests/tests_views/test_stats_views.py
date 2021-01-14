from drf_toolkit.tests import BaseApiTest
from test_app.tests.tests_base import HogwartsTestMixin


class TestStatsView(HogwartsTestMixin, BaseApiTest):
    url = '/houses'

    def setUp(self):
        super().setUp()
        self.houses = self._set_up_houses()
        self.wizards = self._set_up_wizards()
        self._set_up_wizard_houses(wizards=self.wizards, houses=self.houses)

    def test_list_endpoint(self):
        url = f'{self.url}?stats=1'

        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        data = response.json()

        expected = list(reversed(self.expected_stats_houses))
        self.assertEqual(expected, data['results'])

    def test_detail_endpoint(self):
        house = self.houses[0]
        url = f'{self.url}/{house.pk}?stats=1'

        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        data = response.json()
        self.assertEqual(self.expected_stats_houses[0], data)

    def test_list_endpoint_wrong_parameter(self):
        house = self.houses[0]
        url = f'{self.url}/{house.pk}?stats=potato'

        response = self.client.get(url)
        self.assertEqual(400, response.status_code)

        data = response.json()
        self.assertEqual({'stats': "Stats parameter must be an integer"}, data)
