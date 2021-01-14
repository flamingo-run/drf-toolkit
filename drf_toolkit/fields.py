import pytz
from django.conf import settings
from rest_framework.fields import DateTimeField


class DefaultTimezoneDateTimeField(DateTimeField):
    def __init__(self, *args, **kwargs):
        # Prevents that an auto-generated DateTimeField uses the Django's *current* timezone
        # The current timezone can be changed by middleware
        # (eg. the admin can run in -0300, temporarily setting the Django current timezone to -0300)
        default_timezone = pytz.timezone(settings.TIME_ZONE)
        super().__init__(default_timezone=default_timezone, *args, **kwargs)
