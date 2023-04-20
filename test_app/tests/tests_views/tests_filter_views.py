from collections.abc import Iterable

from rest_framework import status

from drf_kit.tests import BaseApiTest
from test_app import models
from test_app.tests.factories.teacher_factories import TeacherFactory
from test_app.tests.tests_base import HogwartsTestMixin


class TestFilterView(HogwartsTestMixin, BaseApiTest):
    url = "/teachers"

    def assertMatched(self, expected: Iterable[models.Teacher], response):
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        expected_ids = {t.pk for t in expected}
        received_ids = {t["id"] for t in response.json()["results"]}
        self.assertEqual(expected_ids, received_ids)

    def test_filter_querystring(self):
        teachers = TeacherFactory.create_batch(5, name="Harry", is_ghost=False)
        TeacherFactory.create_batch(10, name="NotHarry")

        url = f"{self.url}?name=Harry"
        response = self.client.get(url)
        self.assertMatched(expected=teachers, response=response)

    def test_search_body(self):
        teachers = TeacherFactory.create_batch(10, is_half_blood=True)
        TeacherFactory.create_batch(10, is_half_blood=True)
        TeacherFactory.create_batch(10, is_half_blood=False)

        url = f"{self.url}/search"
        search = {"is_half_blood": True, "id": [t.id for t in teachers], "include_unavailable": 1}
        response = self.client.post(url, data=search)
        self.assertMatched(expected=teachers, response=response)
