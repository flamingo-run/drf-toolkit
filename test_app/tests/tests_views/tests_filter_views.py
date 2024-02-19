from rest_framework import status

from drf_kit.tests import BaseApiTest
from test_app.tests.factories.teacher_factories import TeacherFactory
from test_app.tests.tests_base import HogwartsTestMixin


class TestFilterView(HogwartsTestMixin, BaseApiTest):
    url = "/teachers"

    def test_filter_querystring(self):
        teachers = TeacherFactory.create_batch(5, name="Harry", is_ghost=False)
        TeacherFactory.create_batch(10, name="NotHarry")

        url = f"{self.url}?name=Harry"
        response = self.client.get(url)
        self.assertResponseItems(expected_items=teachers, response=response)

    def test_search_body(self):
        teacher = TeacherFactory(is_half_blood=True, is_ghost=False)
        TeacherFactory.create_batch(10, is_half_blood=True, is_ghost=False)
        TeacherFactory.create_batch(10, is_half_blood=False, is_ghost=False)

        url = f"{self.url}/search"
        search = {"is_half_blood": True, "id": teacher.id}
        response = self.client.post(url, data=search)
        self.assertResponseItems(expected_items=[teacher], response=response)

    def test_search_body_with_array(self):
        teachers = TeacherFactory.create_batch(10, is_ghost=False)
        TeacherFactory.create_batch(10, is_ghost=False)

        url = f"{self.url}/search"
        search = {"id": [t.id for t in teachers]}
        response = self.client.post(url, data=search)
        self.assertResponseItems(expected_items=teachers, response=response)

    def test_search_body_empty(self):
        teachers = TeacherFactory.create_batch(10, is_half_blood=True, is_ghost=False)

        url = f"{self.url}/search"
        search = {}
        response = self.client.post(url, data=search)
        self.assertResponseItems(expected_items=teachers, response=response)

    def test_search_body_malformed(self):
        TeacherFactory.create_batch(10, is_half_blood=True, is_ghost=False)

        url = f"{self.url}/search"
        search = "potato"
        response = self.client.post(url, data=search, content_type="application/text")
        self.assertEqual(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, response.status_code)

    def test_search_body_ordered(self):
        teachers = []
        for i in range(10, 20):
            teachers.append(TeacherFactory(id=i, is_ghost=False, picture=None))
        expected_teachers = [self.expected_teacher(teacher) for teacher in teachers]

        for i in range(200, 210):
            TeacherFactory(id=i, is_ghost=True, picture=None)  # noise

        url = f"{self.url}/search?sort=id"
        search = {"is_ghost": False}
        response = self.client.post(url, data=search)

        self.assertResponseList(expected_items=expected_teachers, response=response)
