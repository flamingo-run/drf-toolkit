from drf_kit import filters
from drf_kit.tests import BaseApiTest
from test_app.tests.factories.beast_factories import BeastFactory
from test_app.tests.factories.teacher_factories import TeacherFactory
from test_app.tests.tests_base import HogwartsTestMixin


class TestIntBooleanFilter(HogwartsTestMixin, BaseApiTest):
    url = "/teachers"

    def setUp(self):
        super().setUp()
        self._set_up_teachers()

    def test_filter_true(self):
        url = f"{self.url}?is_half_blood=1"
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)

        results = response.json()["results"]
        self.assertEqual(1, len(results))

    def test_filter_false(self):
        url = f"{self.url}?is_half_blood=0"
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        results = response.json()["results"]
        self.assertEqual(3, len(results))

    def test_filter_fail(self):
        url = f"{self.url}?is_half_blood=yes"
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        results = response.json()["results"]
        self.assertEqual(4, len(results))

    def test_filter_not_boolean(self):
        url = f"{self.url}?is_half_blood=666"
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        results = response.json()["results"]
        self.assertEqual(4, len(results))


class TestIncludeUnavailableFilterSet(HogwartsTestMixin, BaseApiTest):
    url = "/teachers"

    def setUp(self):
        super().setUp()
        self._set_up_teachers()

    def _set_up_teachers(self):
        super()._set_up_teachers()
        self.teachers.append(
            TeacherFactory(
                name="Nicholas de Mimsy-Porpington",
                is_ghost=True,
            ),
        )

    def test_filter_default(self):
        url = f"{self.url}"
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        results = response.json()["results"]
        self.assertEqual(4, len(results))

    def test_filter_true(self):
        url = f"{self.url}?include_unavailable=1"
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        results = response.json()["results"]
        self.assertEqual(5, len(results))

    def test_filter_false(self):
        url = f"{self.url}?include_unavailable=0"
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        results = response.json()["results"]
        self.assertEqual(4, len(results))

    def test_filter_fail(self):
        url = f"{self.url}?include_unavailable=potato"
        response = self.client.get(url)

        self.assertEqual(400, response.status_code)


class TestBackendFilter(HogwartsTestMixin, BaseApiTest):
    def setUp(self):
        super().setUp()
        self._set_up_teachers()
        self._set_up_houses()

    def test_filter_with_wrong_param_type(self):
        url = "/teachers?id=potato"
        response = self.client.get(url)

        self.assertEqual(400, response.status_code)

    def test_filter_with_unknown_param(self):
        url = "/teachers?shining_vampires=no"
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            list(reversed(self.expected_teachers)),
            response.json()["results"],
        )

    def test_filter_with_list_param(self):
        url = "/teachers?id=no"
        response = self.client.get(url)

        self.assertEqual(400, response.status_code)

    def test_order_with_param(self):
        url = "/houses?sort=-name"

        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        data = response.json()

        expected = [
            self.expected_houses[1],
            self.expected_houses[2],
            self.expected_houses[3],
            self.expected_houses[0],
        ]
        self.assertEqual(expected, data["results"])

    def test_order_with_unknown_param(self):
        url = "/houses?ordering=-shining_vampire"
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)

        data = response.json()
        self.assertEqual(len(self.expected_houses), len(data["results"]))

    def test_search_with_param(self):
        url = "/houses?q=yff"

        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        data = response.json()

        expected = [
            self.expected_houses[0],
        ]
        self.assertEqual(expected, data["results"])

    def test_order_search_results(self):
        url = "/houses?q=ff&sort=name"

        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        data = response.json()

        expected = [
            self.expected_houses[0],
            self.expected_houses[3],
        ]
        self.assertEqual(expected, data["results"])

    def test_search_on_disabled_view(self):
        url = "/teachers?q=yff"

        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        data = response.json()
        self.assertEqual(len(self.expected_teachers), len(data["results"]))


class TestNullableFilterSet(HogwartsTestMixin, BaseApiTest):
    url = "/wands"

    def setUp(self):
        super().setUp()
        self._set_up_wands()
        self._set_up_wizards()
        self._assign_wands()

    def _assign_wands(self):
        [wand_not_held, wand_held, *wands] = self.wands

        wand_not_held.holder = None
        wand_not_held.save()
        self._wand_not_held = wand_not_held

        self._wizard = self.wizards[0]
        wand_held.holder = self._wizard
        wand_held.save()
        self._wand_held = wand_held

        for wand in wands:
            wand.holder = self.wizards[1]
            wand.save()

    def test_filter_with_null(self):
        search = "holder_id=null"
        response = self.client.get(f"{self.url}?{search}")
        self.assertEqual(200, response.status_code)

        data = response.json()
        response_ids = [i["id"] for i in data["results"]]

        self.assertEqual([self._wand_not_held.id], response_ids)

    def test_filter_with_null_and_values(self):
        search = f"holder_id=null&holder_id={self._wizard.id}"
        response = self.client.get(f"{self.url}?{search}")
        self.assertEqual(200, response.status_code)

        data = response.json()
        response_ids = [i["id"] for i in data["results"]]

        self.assertEqual(
            [
                self._wand_held.id,
                self._wand_not_held.id,
            ],
            response_ids,
        )

    def test_filter_with_null_invalid_value(self):
        search = "holder_id=nullable"
        response = self.client.get(f"{self.url}?{search}")
        self.assertEqual(400, response.status_code)

        expected_response = ["Field 'id' expected a number but got 'nullable'."]
        self.assertEqual(expected_response, response.json())


class TestAllOfFilter(BaseApiTest):
    def test_raise_exception_when_created_alloffilter_with_conjoined_false(self):
        with self.assertRaisesMessage(ValueError, "AllOfFilter must be conjoined=True"):
            filters.AllOfFilter(conjoined=False)


class TestCallableInitialFilter(BaseApiTest):
    url = "/beasts"

    def test_filter_with_initial_values(self):
        beasts = [
            BeastFactory(is_active=True),
        ]

        BeastFactory(is_active=False)  # noise

        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)

        results = response.json()["results"]
        expected_ids = [b.pk for b in beasts]
        result_ids = [r["id"] for r in results]
        self.assertEqual(expected_ids, list(reversed(result_ids)))

    def test_filter_overwrite_initial_filters(self):
        beasts = [BeastFactory(is_active=False)]

        # noise
        BeastFactory(is_active=True)
        BeastFactory(is_active=True)
        response = self.client.get(self.url, data={"is_active": 0})

        self.assertEqual(200, response.status_code)

        results = response.json()["results"]
        expected_ids = [b.pk for b in beasts]
        result_ids = [r["id"] for r in results]
        self.assertEqual(expected_ids, list(reversed(result_ids)))
