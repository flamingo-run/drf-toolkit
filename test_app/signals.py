from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, pre_save, pre_delete
from django.dispatch import receiver

from drf_kit import signals
from test_app import models, tasks


@receiver(post_save, sender=models.SpellCast)
def notify_minister_of_magic(sender, instance, created, **kwargs):
    tasks.NotifyMinisterOfMagicTask().run()


@receiver(pre_save, sender=models.Wizard)
def check_the_name(sender, instance, **kwargs):
    if instance.name == "Voldemort":
        raise ValidationError("You can't say YOU-KNOW-WHO's name")


@receiver(pre_delete, sender=models.Wizard)
def harry_forever(sender, instance, **kwargs):
    if instance.name == "Harry Potter":
        raise ValidationError("Harry can never die")


@receiver(signals.pre_soft_delete, sender=models.Memory)
def almost_erasing_memory(sender, instance, **kwargs):
    instance.description += " [ERASED]"


@receiver(signals.post_soft_delete, sender=models.Memory)
def memory_has_been_erased(sender, instance, **kwargs):
    tasks.NotifyMinisterOfMagicTask().run(recovered=False)


@receiver(signals.pre_undelete, sender=models.Memory)
def almost_recovering_memory(sender, instance, **kwargs):
    instance.description += " [RECOVERED]"


@receiver(signals.post_undelete, sender=models.Memory)
def memory_has_been_recovered(sender, instance, **kwargs):
    tasks.NotifyMinisterOfMagicTask().run(recovered=True)
