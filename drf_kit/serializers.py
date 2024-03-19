import inspect
import json
import zoneinfo
from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from dateutil import parser
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.backends.postgresql.psycopg_any import Range
from django.db.models.fields.files import FieldFile
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from drf_kit import fields


class BaseModelSerializer(serializers.ModelSerializer):
    @property
    def serializer_field_mapping(self):
        # Overload the auto mapping: Django Field -> DRF Field mapping
        serializer_field_mapping = serializers.ModelSerializer.serializer_field_mapping
        serializer_field_mapping[models.DateTimeField] = fields.DefaultTimezoneDateTimeField
        return serializer_field_mapping

    class Meta:
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

    def get_unique_together_validators(self):
        # Disable DRF UniqueTogetherValidator because the constraint is already enforced at the database level
        # and the exception handler will parse it as status.HTTP_409_CONFLICT
        return []


class ForeignKeyField(PrimaryKeyRelatedField):
    def __init__(self, queryset, write_only=True, m2m=False, **kwargs):
        super().__init__(queryset=queryset, write_only=write_only, **kwargs)
        self.m2m = m2m

    def to_internal_value(self, data):
        if self.m2m:
            return [super().to_internal_value(data=item).pk for item in data]
        return super().to_internal_value(data=data).pk

    def to_representation(self, value):
        if self.m2m:
            return [super().to_representation(item) for item in value]
        return super().to_representation(value)


DATETIME_FORMAT = settings.REST_FRAMEWORK.get("DATETIME_FORMAT", "%Y-%m-%dT%H:%M:%SZ")
DEFAULT_TIMEZONE = zoneinfo.ZoneInfo(settings.TIME_ZONE)


def as_str(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        value = assure_tz(value.astimezone(tz=DEFAULT_TIMEZONE))
        return value.strftime(DATETIME_FORMAT)
    return str(value)


def assure_tz(dt: datetime | str | None, tz: str | ZoneInfo = DEFAULT_TIMEZONE):
    if isinstance(dt, str):
        dt = parser.parse(dt)
    if not dt:
        return dt

    if isinstance(tz, str):
        tz = zoneinfo.ZoneInfo(tz)
    if not dt.tzinfo or dt.tzinfo != tz:
        dt = dt.astimezone(tz=tz)
    return dt


class JSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        if o is None:
            return None
        if isinstance(o, datetime):
            value = assure_tz(o.astimezone(tz=DEFAULT_TIMEZONE))
            return value.strftime(DATETIME_FORMAT)
        if isinstance(o, Decimal):
            return str(o)
        if isinstance(o, ZoneInfo):
            return str(o)
        if issubclass(o.__class__, FieldFile):
            return o.url if bool(o) else None
        if isinstance(o, Range):
            return (o.lower, o.upper)
        if hasattr(o, "_json") and callable(o._json) and not inspect.isclass(o):
            return o._json()
        if hasattr(o, "__dict__"):
            return o.__dict__
        return super().default(o)


def as_dict(items):
    serialized = json.dumps(items, cls=JSONEncoder)
    return json.loads(serialized)
