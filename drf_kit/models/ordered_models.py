import logging

from django.db import models
from django.db.models.signals import pre_save
from django.utils.translation import gettext as _
from ordered_model.models import OrderedModelBase

from drf_kit.models.base_models import BaseModel

logger = logging.getLogger(__name__)


def assert_order(sender, instance, **kwargs):
    # How to prevent the order indexes from becoming sparse:
    # 1. Fetch the list of objects of that grouping, except the current item
    # 2. Insert the current item in the desired index
    #    a. if the current item does not have a specified index, add to the end
    #    b. if it does, add to that index
    # 3. Traverse the list and update each item whose index has changed

    order = getattr(instance, instance.order_field_name)

    group = list(instance.get_ordering_queryset().exclude(id=instance.pk))

    if not getattr(instance, "is_deleted", False):
        if order is not None:  # when updating
            group.insert(max(0, order), instance)
        else:  # when creating
            group.append(instance)

    for index, obj in enumerate(group):
        if obj.pk == instance.pk:
            setattr(instance, instance.order_field_name, index)
        elif obj.order != index:
            # update order without triggering signals
            obj.__class__.objects.filter(pk=obj.pk).update(order=index)


class OrderedModelMixin(OrderedModelBase):
    order = models.PositiveIntegerField(
        db_index=True,
        default=None,
        null=True,
        blank=True,
        verbose_name=_("order"),
    )
    order_field_name = "order"

    class Meta:
        abstract = True
        ordering = ("order", "-updated_at")
        indexes = [
            models.Index(fields=["order"]),
        ]

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        pre_save.connect(assert_order, cls)


class OrderedModel(OrderedModelMixin, BaseModel):
    class Meta(OrderedModelMixin.Meta, BaseModel.Meta):
        abstract = True
        indexes = OrderedModelMixin.Meta.indexes + BaseModel.Meta.indexes
