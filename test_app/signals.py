import warnings

from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver

from drf_kit import signals
from drf_kit.exceptions import ConflictException
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
    warnings.warn("[ERASED]")


@receiver(signals.post_soft_delete, sender=models.Memory)
def memory_has_been_erased(sender, instance, **kwargs):
    tasks.NotifyMinisterOfMagicTask().run(recovered=False)


@receiver(signals.pre_undelete, sender=models.Memory)
def almost_recovering_memory(sender, instance, **kwargs):
    warnings.warn("[RECOVERED]")


@receiver(signals.post_undelete, sender=models.Memory)
def memory_has_been_recovered(sender, instance, **kwargs):
    tasks.NotifyMinisterOfMagicTask().run(recovered=True)


@receiver(pre_save, sender=models.TriWizardPlacement)
def no_prize_duplicated(sender, instance, **kwargs):
    # We could do it with a unique_together constraint, but this is just an example
    # of how to use the ConflictException to perform upserts
    similar_placements = models.TriWizardPlacement.objects.filter(
        prize__startswith=instance.prize,  # non-sense logic to simulate duplicates
    ).exclude(pk=instance.pk)
    if similar_placements:
        raise ConflictException(with_models=similar_placements)
