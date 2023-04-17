import logging
import uuid
from pathlib import Path

logger = logging.getLogger()


class BaseDataStoragePath:
    SUFFIX_DELIMITER = "_"

    @classmethod
    def _build_kwargs(cls, upload_to):
        return {
            "upload_to": upload_to,
        }

    @classmethod
    def rename(cls, filename, new_name=None, unique=True, default_extension=None):
        filepath = Path(filename)
        previous_name = filepath.stem
        extension = filepath.suffix or (f".{default_extension}" if default_extension else None)

        if not extension:
            logger.warning("Saving file without extension")
            extension = ""

        new_name = new_name or previous_name
        if unique:
            suffix = uuid.uuid4()
            new_name = f"{new_name}{cls.SUFFIX_DELIMITER}{suffix}"
        return f"{new_name}{extension}"

    @classmethod
    def _get_pk(cls, instance):
        pk = instance.get("id") if isinstance(instance, dict) else instance.pk

        if not pk:
            pk = uuid.uuid4()
        return str(pk)
