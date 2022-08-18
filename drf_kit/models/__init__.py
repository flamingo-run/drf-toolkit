from drf_kit.managers import SoftDeleteAvailabilityManager, SoftDeleteOrderedManager
from drf_kit.models.availability_models import AvailabilityModel, AvailabilityModelMixin
from drf_kit.models.base_models import BaseModel
from drf_kit.models.diff_models import ModelDiffMixin
from drf_kit.models.file_models import BoundedFileMixin
from drf_kit.models.inheritance_models import InheritanceModel, InheritanceModelMixin
from drf_kit.models.ordered_models import OrderedModel, OrderedModelMixin
from drf_kit.models.soft_delete_models import SoftDeleteModel, SoftDeleteModelMixin


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


class SoftDeleteAvailabilityModel(SoftDeleteModelMixin, AvailabilityModelMixin, BaseModel):
    objects = SoftDeleteAvailabilityManager()

    class Meta(SoftDeleteModelMixin.Meta, AvailabilityModelMixin.Meta, BaseModel.Meta):
        abstract = True
        indexes = SoftDeleteModelMixin.Meta.indexes + AvailabilityModelMixin.Meta.indexes + BaseModel.Meta.indexes


class InheritanceOrderedModel(OrderedModelMixin, InheritanceModelMixin, BaseModel):
    class Meta(OrderedModelMixin.Meta, InheritanceModelMixin.Meta, BaseModel.Meta):
        abstract = True
        indexes = OrderedModelMixin.Meta.indexes + BaseModel.Meta.indexes


__all__ = (
    "ModelDiffMixin",
    "BoundedFileMixin",
    "BaseModel",
    "SoftDeleteModel",
    "OrderedModel",
    "InheritanceModel",
    "SoftDeleteInheritanceOrderedModel",
    "SoftDeleteInheritanceModel",
    "SoftDeleteOrderedModel",
    "SoftDeleteAvailabilityModel",
    "InheritanceOrderedModel",
    "AvailabilityModel",
    "AvailabilityModelMixin",
)
