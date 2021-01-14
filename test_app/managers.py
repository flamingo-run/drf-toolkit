from django.db import models


class AvailableManager(models.Manager):
    def get_filter(self):
        return models.Q(is_ghost=False)

    def get_queryset(self):
        return super().get_queryset().filter(self.get_filter())
