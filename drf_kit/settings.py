from django.conf import settings
from rest_framework.settings import APISettings

USER_SETTINGS = getattr(settings, "REST_FRAMEWORK_TOOLKIT", None)

DEFAULTS = {
    "DEFAULT_BODY_CACHE_KEY_FUNC": "drf_kit.cache.body_cache_key_constructor",
}

IMPORT_STRINGS = [
    "DEFAULT_BODY_CACHE_KEY_FUNC",
]

toolkit_api_settings = APISettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS)
