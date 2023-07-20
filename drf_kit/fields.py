import pytz
from django.conf import settings
from django.db.models import SlugField
from django.utils.text import slugify
from rest_framework.fields import DateTimeField


class DefaultTimezoneDateTimeField(DateTimeField):
    def __init__(self, *args, **kwargs):
        # Prevents that an auto-generated DateTimeField uses the Django's *current* timezone
        # The current timezone can be changed by middleware
        # (e.g. the admin can run in -0300, temporarily setting the Django current timezone to -0300)
        default_timezone = pytz.timezone(settings.TIME_ZONE)
        super().__init__(default_timezone=default_timezone, *args, **kwargs)


class SlugifyField(SlugField):
    def __init__(self, max_length=50, db_index=True, allow_unicode=False, func=slugify, **kwargs):
        self.func = func
        super().__init__(max_length=max_length, db_index=db_index, allow_unicode=allow_unicode, **kwargs)

    def pre_save(self, model_instance, add):
        value = super().pre_save(model_instance, add)
        return self.func(value)
