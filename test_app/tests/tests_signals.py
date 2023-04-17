import warnings
from unittest.mock import patch

from django.db.models.signals import post_save

from drf_kit.signals import UnplugSignal
from drf_kit.tests import BaseApiTest
from test_app import models, signals
from test_app.tests.factories.memory_factories import MemoryFactory
from test_app.tests.factories.spell_cast_factories import CombatSpellCastFactory
from test_app.tests.factories.spell_factories import SpellFactory
from test_app.tests.factories.wizard_factories import WizardFactory
from test_app.tests.tests_base import HogwartsTestMixin


class TestUnplugSignal(BaseApiTest):
    def patch_signal_trigger(self, **kwargs):
        return patch("test_app.tasks.NotifyMinisterOfMagicTask.run", **kwargs)

    def unplug(self):
        return UnplugSignal(
            signal=post_save,
            func=signals.notify_minister_of_magic,
            model=models.SpellCast,
        )

    def test_preserve_signal(self):
        wizard = WizardFactory(name="Harry Potter")
        spell = SpellFactory(name="Expecto Patronum")

        with self.patch_signal_trigger() as patched_signal:
            spell_cast = CombatSpellCastFactory(
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
        self._set_up_wizards()

    def patch_notify_task(self):
        return patch("test_app.tasks.NotifyMinisterOfMagicTask.run")

    def test_soft_delete_model(self):
        memory = MemoryFactory()

        with self.patch_notify_task() as some_task, warnings.catch_warnings(record=True) as warn:
            memory.delete()

        self.assertEqual("[ERASED]", str(warn[-1].message))
        some_task.assert_called_once_with(recovered=False)

    def test_undelete_model(self):
        memory = MemoryFactory()
        memory.delete()
        memory.refresh_from_db()

        with self.patch_notify_task() as some_task, warnings.catch_warnings(record=True) as warn:
            memory.undelete()

        self.assertEqual("[RECOVERED]", str(warn[0].message))
        some_task.assert_called_once_with(recovered=True)
