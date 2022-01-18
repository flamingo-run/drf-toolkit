import logging

from django.db import models
from drf_kit.models.base_models import BaseModel

logger = logging.getLogger(__name__)


class InheritanceModelMixin(models.Model):
    type = models.CharField(
        max_length=100,
    )

    class Meta(BaseModel.Meta):
        abstract = True
        indexes = []

    def save(self, *args, **kwargs):
        self.type = self.__class__.__name__.lower()
        return super().save(*args, **kwargs)


class InheritanceModel(InheritanceModelMixin, BaseModel):
    class Meta(InheritanceModelMixin.Meta, BaseModel.Meta):
        abstract = True
