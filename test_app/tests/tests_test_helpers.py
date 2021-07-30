from unittest.mock import patch

from drf_kit.tests import BaseApiTest
from test_app import tasks


class TestPendingMigrations(BaseApiTest):
    def _mock_command(self, error=False):
        def call_command(*args, **kwargs):
            output = "No changes found" if not error else "Pending migrations"
            kwargs["stdout"].write(output)
            if error:
                raise SystemExit()

        return patch("drf_kit.tests.call_command", side_effect=call_command)

    def test_migrations_done(self):
        with self._mock_command(error=False) as mocked:
            self.assertNoPendingMigration("test_app")

            command, app_name, param_a, param_b = mocked.call_args[0]

            self.assertEqual("makemigrations", command)
            self.assertEqual("test_app", app_name)
            self.assertEqual("--check", param_a)
            self.assertEqual("--dry-run", param_b)

    def test_migrations_missing(self):
        with self._mock_command(error=True) as mocked:
            with self.assertRaises(AssertionError):
                self.assertNoPendingMigration("test_app")

            mocked.assert_called_once()


class TestLockAssertion(BaseApiTest):
    def test_assert_locked_with_parameters(self):
        with self.patch_cache_lock() as lock:
            tasks.LockableTask().run()

        lock.assert_called_with("triwizard", timeout=42)

    def test_assert_locked_with_wrong_args(self):
        with self.patch_cache_lock() as lock:
            tasks.LockableTask().run()

        expected_message = "Expected to lock with quidditch, but locked with triwizard"
        with self.assertRaisesMessage(AssertionError, expected_message=expected_message):
            lock.assert_called_with("quidditch", timeout=42)

    def test_assert_locked_with_wrong_kwargs(self):
        with self.patch_cache_lock() as lock:
            tasks.LockableTask().run()

        expected_message = "Expected to lock with timeout=666, but locked with 42"
        with self.assertRaisesMessage(AssertionError, expected_message=expected_message):
            lock.assert_called_with("triwizard", timeout=666)

    def test_assert_locked_with_wrong_args_amount(self):
        with self.patch_cache_lock() as lock:
            tasks.LockableTask().run()

        expected_message = "Expected to lock with 2 args: triwizard, inconvenient. But locked with 1 args: triwizard"
        with self.assertRaisesMessage(AssertionError, expected_message=expected_message):
            lock.assert_called_with("triwizard", "inconvenient", timeout=42)

    def test_assert_locked_with_wrong_kwargs_amount(self):
        with self.patch_cache_lock() as lock:
            tasks.LockableTask().run()

        expected_message = "Expected to lock with 2 kwargs: timeout, inconvenient. But locked with 1 kwargs: timeout"
        with self.assertRaisesMessage(AssertionError, expected_message=expected_message):
            lock.assert_called_with("triwizard", timeout=42, inconvenient=55)

    def test_assert_locked_when_locked(self):
        with self.patch_cache_lock() as lock:
            tasks.LockableTask().run()

        lock.assert_called()

    def test_assert_locked_when_not_locked(self):
        with self.patch_cache_lock() as lock:
            tasks.NotifyMinisterOfMagicTask().run()

        expected_message = "Expected to be called, but it was not"
        with self.assertRaisesMessage(AssertionError, expected_message=expected_message):
            lock.assert_called_with()

    def test_execute_side_effect(self):
        def _effect():
            raise Exception("Dementors")

        with self.patch_cache_lock(side_effect=_effect) as lock:
            with self.assertRaisesMessage(Exception, expected_message="Dementors"):
                tasks.LockableTask().run()

        lock.assert_called()

    def test_use_with_start(self):
        lock = self.patch_cache_lock()
        lock.start()

        tasks.LockableTask().run()
        lock.assert_called()

        lock.stop()
