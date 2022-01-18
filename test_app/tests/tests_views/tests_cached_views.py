from unittest.mock import patch

from django.core.cache import cache
from rest_framework import status

from drf_kit.cache import CacheResponse
from drf_kit.tests import BaseApiTest
from test_app.tests.tests_base import HogwartsTestMixin


class TestCachedView(HogwartsTestMixin, BaseApiTest):
    url = "/teachers"

    def setUp(self):
        super().setUp()
        self._set_up_teachers()

    def test_cache_headers_endpoint(self):
        url = self.url

        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("MISS", response["X-Cache"])

        cached_response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, cached_response.status_code)
        self.assertEqual("HIT", cached_response["X-Cache"])

    def test_retrocompatible(self):
        url = self.url

        key_method = CacheResponse().calculate_key
        with patch("drf_kit.cache.CacheResponse.calculate_key", wraps=key_method) as calc:
            # Call the first time to get the response
            response = self.client.get(url)

            # Call again the key creation method to extract the cache key
            call_kwargs = calc.mock_calls[0][2]
            key = key_method(**call_kwargs)

        with self.real_cache():
            # In older DRF versions, the view cache is the whole response object
            cache.set(key, response)

            # Call again, hoping for a cache hit
            cached_response = self.client.get(url)
            self.assertEqual("HIT", cached_response["X-Cache"])

            self.assertEqual(response.json(), cached_response.json())

    def test_cache_by_using_content_type(self):
        url = self.url

        response_json_miss = self.client.get(url, HTTP_ACCEPT="application/json")
        self.assertEqual(status.HTTP_200_OK, response_json_miss.status_code)
        self.assertEqual("MISS", response_json_miss["X-Cache"])

        response_html_miss = self.client.get(url, HTTP_ACCEPT="text/html")
        self.assertEqual(status.HTTP_200_OK, response_html_miss.status_code)
        self.assertEqual("MISS", response_html_miss["X-Cache"])

        response_json_hit = self.client.get(url, HTTP_ACCEPT="application/json")
        self.assertEqual(status.HTTP_200_OK, response_json_hit.status_code)
        self.assertEqual("HIT", response_json_hit["X-Cache"])
        self.assertEqual(response_json_miss.content, response_json_hit.content)

        response_html_hit = self.client.get(url, HTTP_ACCEPT="text/html")
        self.assertEqual(status.HTTP_200_OK, response_html_hit.status_code)
        self.assertEqual("HIT", response_html_hit["X-Cache"])

    def test_cache_control_no_cache(self):
        url = self.url
        cache_control = "no-cache"
        response_json_miss = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response_json_miss.status_code)
        self.assertEqual("MISS", response_json_miss["X-Cache"])
        self.assertEqual(None, response_json_miss.get("Cache-Control"))

        response_json_miss = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response_json_miss.status_code)
        self.assertEqual("HIT", response_json_miss["X-Cache"])
        self.assertEqual(None, response_json_miss.get("Cache-Control"))

        response_json_miss = self.client.get(url, HTTP_CACHE_CONTROL=cache_control)
        self.assertEqual(status.HTTP_200_OK, response_json_miss.status_code)
        self.assertEqual("MISS", response_json_miss["X-Cache"])
        self.assertEqual("max-age=300", response_json_miss.get("Cache-Control"))

        cache_control = "no-store,no-cache"
        response_json_miss = self.client.get(url, HTTP_CACHE_CONTROL=cache_control)
        self.assertEqual(status.HTTP_200_OK, response_json_miss.status_code)
        self.assertEqual("MISS", response_json_miss["X-Cache"])
        self.assertEqual("max-age=300", response_json_miss.get("Cache-Control"))

    def test_cache_control_invalid_directive(self):
        url = self.url
        cache_control = "invalid-directive"
        response_json_miss = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response_json_miss.status_code)
        self.assertEqual("MISS", response_json_miss["X-Cache"])
        self.assertEqual(None, response_json_miss.get("Cache-Control"))

        response_json_miss = self.client.get(url, **{"cache-control": cache_control})
        self.assertEqual(status.HTTP_200_OK, response_json_miss.status_code)
        self.assertEqual("HIT", response_json_miss["X-Cache"])
        self.assertEqual(None, response_json_miss.get("Cache-Control"))
