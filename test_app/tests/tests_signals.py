from unittest.mock import patch

from django.db.models.signals import post_save

from drf_kit.signals import UnplugSignal
from drf_kit.tests import BaseApiTest
from test_app import signals, models
from test_app.models import Wizard, Spell, SpellCast
from test_app.tests.tests_base import HogwartsTestMixin


class TestUnplugSignal(BaseApiTest):
    def patch_signal_trigger(self, **kwargs):
        return patch('test_app.tasks.NotifyMinisterOfMagicTask.run', **kwargs)

    def unplug(self):
        return UnplugSignal(
            signal=post_save,
            func=signals.notify_minister_of_magic,
            model=models.SpellCast,
        )

    def test_preserve_signal(self):
        wizard = Wizard.objects.create(name="Harry Potter")
        spell = Spell.objects.create(name="Expecto Patronum")

        with self.patch_signal_trigger() as patched_signal:
            spell_cast = SpellCast.objects.create(
                wizard=wizard,
                spell=spell,
            )
            self.assertEqual(1, patched_signal.call_count)

            with self.unplug():
                spell_cast.is_successful = False
                spell_cast.save()

            self.assertEqual(1, patched_signal.call_count)

            spell_cast.is_successful = True
            spell_cast.save()
            self.assertEqual(2, patched_signal.call_count)


class TestSoftDeleteSignals(HogwartsTestMixin, BaseApiTest):
    def setUp(self):
        super().setUp()
        self.wizards = self._set_up_wizards()

    def patch_notify_task(self):
        return patch('test_app.tasks.NotifyMinisterOfMagicTask.run')

    def test_soft_delete_model(self):
        memory = models.Memory.objects.create(owner=self.wizards[0])

        with self.patch_notify_task() as some_task:
            memory.delete()

        some_task.assert_called_once_with(recovered=False)

        memory.refresh_from_db()
        self.assertIn('[ERASED]', memory.description)

    def test_undelete_model(self):
        memory = models.Memory.objects.create(owner=self.wizards[0])
        memory.delete()

        with self.patch_notify_task() as some_task:
            memory.undelete()

        some_task.assert_called_once_with(recovered=True)

        memory.refresh_from_db()
        self.assertIn('[RECOVERED]', memory.description)
