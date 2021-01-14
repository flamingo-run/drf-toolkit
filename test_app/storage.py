from drf_toolkit.storage import BaseDataStoragePath


class StoragePath(BaseDataStoragePath):
    @classmethod
    def _media_thumb_upload(cls, instance, filename):
        if not filename:
            return None
        parts = [
            'wizard',
            cls._get_pk(instance),
            cls.rename(filename, 'thumb'),
        ]
        return '/'.join(parts)

    @classmethod
    def media_thumb(cls):
        return cls._build_kwargs(
            upload_to=cls._media_thumb_upload,
        )
