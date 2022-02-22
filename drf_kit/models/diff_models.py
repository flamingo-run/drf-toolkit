import logging
from django.forms.models import model_to_dict

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
        return as_dict(
            {
                _field_name(field): field.value_from_object(self)
                for field in self._meta.fields
                if getattr(field, "editable", False)
            }
        )


def _field_name(field):
    if field.is_relation:
        return f"{field.name}_id"
    return field.name
