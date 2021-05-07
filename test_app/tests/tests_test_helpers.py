from unittest.mock import patch

from drf_kit.tests import BaseApiTest


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
