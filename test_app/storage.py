from drf_kit.storage import BaseDataStoragePath


class StoragePath(BaseDataStoragePath):
    @classmethod
    def _media_thumb_upload(cls, instance, filename):
        if not filename:
            return None
        parts = [
            "wizard",
            cls._get_pk(instance),
            cls.rename(filename, "thumb", default_extension="jpeg"),
        ]
        return "/".join(parts)

    @classmethod
    def media_thumb(cls):
        return cls._build_kwargs(
            upload_to=cls._media_thumb_upload,
        )

    @classmethod
    def _preserve_name_upload(cls, instance, filename):
        if not filename:
            return None
        parts = [
            "wizard",
            cls._get_pk(instance),
            cls.rename(filename),
        ]
        return "/".join(parts)

    @classmethod
    def another_pic(cls):
        return cls._build_kwargs(
            upload_to=cls._preserve_name_upload,
        )
