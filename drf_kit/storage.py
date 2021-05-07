import uuid
from pathlib import Path

from django.core.exceptions import ValidationError


class BaseDataStoragePath:
    SUFFIX_DELIMITER = "_"

    @classmethod
    def _build_kwargs(cls, upload_to):
        return {
            "upload_to": upload_to,
        }

    @classmethod
    def rename(cls, filename, new_name=None, unique=True):
        filepath = Path(filename)
        previous_name = filepath.stem
        extension = filepath.suffix

        if not extension:
            raise ValidationError("Filename must have and extension")

        new_name = new_name or previous_name
        if unique:
            suffix = uuid.uuid4()
            new_name = f"{new_name}{cls.SUFFIX_DELIMITER}{suffix}"
        return f"{new_name}{extension}"

    @classmethod
    def _get_pk(cls, instance):
        if isinstance(instance, dict):
            pk = instance.get("id")
        else:
            pk = instance.pk

        if not pk:
            pk = uuid.uuid4()
        return str(pk)
