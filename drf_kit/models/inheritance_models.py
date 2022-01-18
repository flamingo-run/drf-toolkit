import logging

from django.db import models
from django.db.models.signals import pre_save

from drf_kit.models.base_models import BaseModel

logger = logging.getLogger(__name__)


def assert_inherited_type(sender, instance, **kwargs):
    instance.type = instance.__class__.__name__.lower()


class InheritanceModelMixin(models.Model):
    type = models.CharField(
        max_length=100,
    )

    class Meta(BaseModel.Meta):
        abstract = True
        indexes = []

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        pre_save.connect(assert_inherited_type, cls)


class InheritanceModel(InheritanceModelMixin, BaseModel):
    class Meta(InheritanceModelMixin.Meta, BaseModel.Meta):
        abstract = True
