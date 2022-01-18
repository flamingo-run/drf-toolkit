import logging

from django.db import models
from django.utils.translation import ugettext as _
from ordered_model.models import OrderedModelBase

from drf_kit.models.base_models import BaseModel

logger = logging.getLogger(__name__)


class OrderedModelMixin(OrderedModelBase):
    order = models.PositiveIntegerField(
        db_index=True,
        default=None,
        null=True,
        blank=True,
        verbose_name=_("order"),
    )
    order_field_name = "order"

    def save(self, *args, **kwargs):
        if kwargs.pop("ignore_order_validation", False):
            return super().save(*args, **kwargs)

        # How to prevent the order indexes from becoming sparse:
        # 1. Fetch the list of objects of that grouping, except the current item
        # 2. Insert the current item in the desired index
        #    a. if the current item does not have a specified index, add to the end
        #    b. if it does, add to that index
        # 3. Traverse the list and update each item whose index has changed

        order = getattr(self, self.order_field_name)

        group = list(self.get_ordering_queryset().exclude(id=self.pk))

        if order is not None:  # when updating
            group.insert(max(0, order), self)
        else:  # when creating
            group.append(self)

        for index, obj in enumerate(group):
            if obj.pk == self.pk:
                setattr(self, self.order_field_name, index)
            elif obj.order != index:
                obj.order = index
                obj.save(ignore_order_validation=True)

        return super().save(*args, **kwargs)

    class Meta:
        abstract = True
        ordering = ("order", "-updated_at")


class OrderedModel(OrderedModelMixin, BaseModel):
    class Meta(OrderedModelMixin.Meta, BaseModel.Meta):
        abstract = True
