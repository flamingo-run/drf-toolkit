from drf_kit.tests import BaseApiTest
from test_app.tests.tests_base import HogwartsTestMixin


class TestContentTypeView(HogwartsTestMixin, BaseApiTest):
    url = "/wizards"

    def test_default_content_type(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

        self.assertEqual("application/json", response["Content-Type"])

    def test_browser_content_type(self):
        response = self.client.get(self.url, HTTP_ACCEPT="text/html")
        self.assertEqual(200, response.status_code)

        self.assertEqual("text/html; charset=utf-8", response["Content-Type"])

    def test_unsupported_content_type(self):
        response = self.client.get(self.url, HTTP_ACCEPT="text/plain")
        self.assertEqual(406, response.status_code)
