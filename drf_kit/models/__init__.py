from drf_kit.models.diff_models import ModelDiffMixin
from drf_kit.models.file_models import BoundedFileMixin
from drf_kit.models.base_models import BaseModel
from drf_kit.models.soft_delete_models import SoftDeleteModel, SoftDeleteModelMixin
from drf_kit.models.ordered_models import (  # pylint: disable=reimported
    OrderedModel,
    OrderedModelMixin,
    OrderedModel as BaseOrderedModel,  # retro-compatibility
)
from drf_kit.models.inheritance_models import InheritanceModel, InheritanceModelMixin
from drf_kit.managers import SoftDeleteOrderedManager


class SoftDeleteInheritanceOrderedModel(SoftDeleteModelMixin, OrderedModelMixin, InheritanceModelMixin, BaseModel):
    objects = SoftDeleteOrderedManager()

    class Meta(SoftDeleteModelMixin.Meta, OrderedModelMixin.Meta, InheritanceModelMixin.Meta, BaseModel.Meta):
        abstract = True
        indexes = SoftDeleteModelMixin.Meta.indexes + OrderedModelMixin.Meta.indexes + BaseModel.Meta.indexes


class SoftDeleteInheritanceModel(SoftDeleteModelMixin, InheritanceModelMixin, BaseModel):
    class Meta(SoftDeleteModelMixin.Meta, InheritanceModelMixin.Meta, BaseModel.Meta):
        abstract = True
        indexes = SoftDeleteModelMixin.Meta.indexes + BaseModel.Meta.indexes


class SoftDeleteOrderedModel(SoftDeleteModelMixin, OrderedModelMixin, BaseModel):
    objects = SoftDeleteOrderedManager()

    class Meta(SoftDeleteModelMixin.Meta, OrderedModelMixin.Meta, BaseModel.Meta):
        abstract = True
        indexes = SoftDeleteModelMixin.Meta.indexes + OrderedModelMixin.Meta.indexes + BaseModel.Meta.indexes


class InheritanceOrderedModel(OrderedModelMixin, InheritanceModelMixin, BaseModel):
    class Meta(OrderedModelMixin.Meta, InheritanceModelMixin.Meta, BaseModel.Meta):
        abstract = True
        indexes = OrderedModelMixin.Meta.indexes + BaseModel.Meta.indexes


__all__ = (
    "ModelDiffMixin",
    "BoundedFileMixin",
    "BaseModel",
    "SoftDeleteModel",
    "BaseOrderedModel",
    "OrderedModel",
    "InheritanceModel",
    "SoftDeleteInheritanceOrderedModel",
    "SoftDeleteInheritanceModel",
    "SoftDeleteOrderedModel",
    "InheritanceOrderedModel",
)
