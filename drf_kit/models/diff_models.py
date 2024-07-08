import contextlib
import logging

from django.db.models import GeneratedField

from drf_kit.serializers import as_dict

logger = logging.getLogger(__name__)


class ModelDiffMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._initial = self._dict

    @property
    def _diff(self):
        initial_dict = self._initial
        current_dict = self._dict
        diffs = [(k, (v, current_dict[k])) for k, v in initial_dict.items() if v != current_dict[k]]
        return dict(diffs)

    @property
    def _has_changed(self):
        return bool(self._diff)

    @property
    def _changed_fields(self):
        return self._diff.keys()

    def _get_field_diff(self, field_name):
        return self._diff.get(field_name, None)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._initial = self._dict

    @property
    def _dict(self):
        # ref: https://github.com/django/django/blob/4.0.2/django/forms/models.py#L86
        data = {}

        # If there's any deferred field (i.e. lazy loading),
        # refresh the whole object at once, instead of letting `value_from_object` refresh one by one
        # TODO: Lazily compute the diff only for the deferred fields, otherwise .only() will be useless
        lazy_fields = []
        deferred_fields = self.get_deferred_fields()
        for field in self._meta.get_fields():
            if isinstance(field, GeneratedField):
                continue
            if field.name in deferred_fields:
                lazy_fields.append(field)

        if lazy_fields:
            # refresh_from_db() will populate the deferred fields, this is causing max-recursing error,
            # so we refresh all of them at once
            self.refresh_from_db(fields=[field.attname for field in self._meta.concrete_fields])

        for field in self._meta.fields:
            if not getattr(field, "editable", False):
                continue
            serializable_value = field.value_from_object(self)
            with contextlib.suppress(Exception):
                serializable_value = field.get_prep_value(value=serializable_value)

            data[_field_name(field)] = serializable_value

        return as_dict(data)


def _field_name(field):
    if field.is_relation:
        return f"{field.name}_id"
    return field.name
