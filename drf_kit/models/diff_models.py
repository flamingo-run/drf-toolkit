import logging

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
        for field in self._meta.fields:
            if not getattr(field, "editable", False):
                continue
            serializable_value = field.value_from_object(self)
            try:
                serializable_value = field.get_prep_value(value=serializable_value)
            except Exception:  # pylint: disable=broad-except
                # The prep-value might fail because Django performs a check
                # (eg. the field cannot be empty)
                # But we don't really care for that, we just want their serializable versions
                # and not necessarily their database-compliant versions
                ...
            data[_field_name(field)] = serializable_value

        return as_dict(data)


def _field_name(field):
    if field.is_relation:
        return f"{field.name}_id"
    return field.name
