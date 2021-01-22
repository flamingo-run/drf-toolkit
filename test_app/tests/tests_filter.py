from drf_kit.tests import BaseApiTest
from test_app import models
from test_app.tests.tests_base import HogwartsTestMixin


class TestIntBooleanFilter(HogwartsTestMixin, BaseApiTest):
    url = '/teachers'

    def setUp(self):
        super().setUp()
        self.teachers = self._set_up_teachers()

    def test_filter_true(self):
        url = f'{self.url}?is_half_blood=1'
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)

        results = response.json()['results']
        self.assertEqual(1, len(results))

    def test_filter_false(self):
        url = f'{self.url}?is_half_blood=0'
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        results = response.json()['results']
        self.assertEqual(3, len(results))

    def test_filter_fail(self):
        url = f'{self.url}?is_half_blood=yes'
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        results = response.json()['results']
        self.assertEqual(4, len(results))

    def test_filter_not_boolean(self):
        url = f'{self.url}?is_half_blood=666'
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        results = response.json()['results']
        self.assertEqual(4, len(results))


class TestIncludeUnavailableFilterSet(HogwartsTestMixin, BaseApiTest):
    url = '/teachers'

    def setUp(self):
        super().setUp()
        self.teachers = self._set_up_teachers()

    def _set_up_teachers(self):
        teachers = super()._set_up_teachers()
        teachers.append(
            models.Teacher.objects.create(
                name="Nicholas de Mimsy-Porpington",
                is_ghost=True,
            )
        )
        return teachers

    def test_filter_default(self):
        url = f'{self.url}'
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        results = response.json()['results']
        self.assertEqual(4, len(results))

    def test_filter_true(self):
        url = f'{self.url}?include_unavailable=1'
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        results = response.json()['results']
        self.assertEqual(5, len(results))

    def test_filter_false(self):
        url = f'{self.url}?include_unavailable=0'
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        results = response.json()['results']
        self.assertEqual(4, len(results))

    def test_filter_fail(self):
        url = f'{self.url}?include_unavailable=potato'
        response = self.client.get(url)

        self.assertEqual(400, response.status_code)


class TestBackendFilter(HogwartsTestMixin, BaseApiTest):
    def setUp(self):
        super().setUp()
        self.teachers = self._set_up_teachers()
        self.teachers = self._set_up_houses()

    def test_filter_with_wrong_param_type(self):
        url = f'/teachers?id=potato'
        response = self.client.get(url)

        self.assertEqual(400, response.status_code)

    def test_filter_with_unknown_param(self):
        url = f'/teachers?shining_vampires=no'
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            list(reversed(self.expected_teachers)),
            response.json()['results'],
        )

    def test_filter_with_list_param(self):
        url = f'/teachers?id=no'
        response = self.client.get(url)

        self.assertEqual(400, response.status_code)

    def test_order_with_param(self):
        url = f'/houses?sort=-name'

        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        data = response.json()

        expected = [
            self.expected_houses[1],
            self.expected_houses[2],
            self.expected_houses[3],
            self.expected_houses[0],
        ]
        self.assertEqual(expected, data['results'])

    def test_order_with_unknown_param(self):
        url = f'/houses?ordering=-shining_vampire'
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)

        data = response.json()
        self.assertEqual(len(self.expected_houses), len(data['results']))

    def test_search_with_param(self):
        url = f'/houses?q=yff'

        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        data = response.json()

        expected = [
            self.expected_houses[0],
        ]
        self.assertEqual(expected, data['results'])

    def test_order_search_results(self):
        url = f'/houses?q=ff&sort=name'

        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        data = response.json()

        expected = [
            self.expected_houses[0],
            self.expected_houses[3],
        ]
        self.assertEqual(expected, data['results'])

    def test_search_on_disabled_view(self):
        url = f'/teachers?q=yff'

        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        data = response.json()
        self.assertEqual(len(self.expected_teachers), len(data['results']))
