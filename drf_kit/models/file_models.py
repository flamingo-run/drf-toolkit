import logging
from pathlib import Path

from django.db import models

logger = logging.getLogger(__name__)


class BoundedFileMixin:
    def save(self, *args, **kwargs):
        being_created = self.pk is None

        super().save(*args, **kwargs)

        if not being_created:
            return

        file_fields = [f for f in self._meta.get_fields() if isinstance(f, models.FileField)]

        if file_fields:
            changed = False
            for field in file_fields:
                file = getattr(self, field.name)
                if file:
                    old_file = file.name
                    new_file = file.field.generate_filename(self, Path(old_file).name)

                    if new_file != old_file:
                        changed = True

                        if hasattr(file.storage, "move"):
                            file.storage.move(previous_name=old_file, new_name=new_file)
                        else:  # still works when using local filesystem
                            file.storage.save(new_file, file)
                            file.storage.delete(old_file)
                        file.name = new_file
                        file.close()

            if changed:
                kwargs.pop("force_insert", None)
                super().save(*args, **kwargs)
