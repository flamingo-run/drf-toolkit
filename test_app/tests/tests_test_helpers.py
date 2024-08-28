import re
from datetime import UTC, datetime
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

    def test_execute_lock_side_effect_callable(self):
        def _effect():
            raise ValueError("Dementors")

        with (
            self.patch_cache_lock(lock_side_effect=_effect) as lock,
            self.assertRaisesMessage(ValueError, expected_message="Dementors"),
        ):
            tasks.LockableTask().run()

        lock.assert_called()

    def test_execute_lock_side_effect_error(self):
        effect = Exception("Dementors")

        with (
            self.patch_cache_lock(lock_side_effect=effect) as lock,
            self.assertRaisesMessage(Exception, expected_message="Dementors"),
        ):
            tasks.LockableTask().run()

        lock.assert_called()

    def test_execute_lock_side_effect_error_class(self):
        effect = Exception

        with self.patch_cache_lock(lock_side_effect=effect) as lock, self.assertRaises(Exception):
            tasks.LockableTask().run()

        lock.assert_called()

    def test_execute_unlock_side_effect(self):
        def _effect():
            raise ValueError("Dementors")

        with (
            self.patch_cache_lock(unlock_side_effect=_effect) as lock,
            self.assertRaisesMessage(ValueError, expected_message="Dementors"),
        ):
            tasks.LockableTask().run()

        lock.assert_called()

    def test_use_with_start(self):
        lock = self.patch_cache_lock()
        lock.start()

        tasks.LockableTask().run()
        lock.assert_called()

        lock.stop()


class TestResponseMatch(BaseApiTest):
    def _assert_match(self, expected, received):
        self.assertResponseMatch(expected=expected, received=received)

    def _assert_not_match(self, expected, received, expected_error):
        with self.assertRaisesMessage(expected_exception=AssertionError, expected_message=expected_error):
            self.assertResponseMatch(expected=expected, received=received)

    def test_match_types(self):
        expected = {"name": "Harry", "age": 13}

        received = {"name": "Harry", "age": 13}
        self._assert_match(expected, received)

        received = {"name": "Potter", "age": 13}
        message = "There's 1 fields that differ\n- name: Received `Potter`, but expected `Harry` "
        self._assert_not_match(expected, received, message)

    def test_match_equivalent_types(self):
        expected = {"name": "Harry", "muggle": True}

        received = {"name": "Harry", "muggle": True}
        self._assert_match(expected, received)

        received = {"name": "Harry", "muggle": 1}
        message = "There's 1 fields that differ\n- muggle: Received `<class 'int'>`, but expected `<class 'bool'>` "
        self._assert_not_match(expected, received, message)

    def test_match_regex(self):
        expected = {"name": re.compile("H.*y"), "age": 13}

        received = {"name": "Harry", "age": 13}
        self._assert_match(expected, received)

        received = {"name": "Potter", "age": 13}
        message = "There's 1 fields that differ\n- name: Received `Potter`, but expected to match `H.*y` "
        self._assert_not_match(expected, received, message)

    def test_match_embedded(self):
        expected = {"name": "Harry", "age": {"amount": 13, "min_age": 0}}

        received = {"name": "Harry", "age": {"amount": 13, "min_age": 0}}
        self._assert_match(expected, received)

        received = {"name": "Harry", "age": {"amount": 13}}
        message = "There's 1 fields that differ\n- age: There's 1 fields missing: min_age "
        self._assert_not_match(expected, received, message)

        received = {"name": "Harry", "age": {"amount": 13, "min_age": 0, "max_age": 100}}
        message = "There's 1 fields that differ\n- age: There's 1 unexpected fields: max_age "
        self._assert_not_match(expected, received, message)

        received = {"name": "Harry", "age": 13}
        message = "There's 1 fields that differ\n- age: Received `<class 'int'>`, but expected `<class 'dict'>`"
        self._assert_not_match(expected, received, message)

    def test_match_embedded_list(self):
        expected = {"name": "Harry", "friends": [{"name": "Hermione", "age": 13}, {"name": "Hagrid", "age": 50}]}

        received = {"name": "Harry", "friends": [{"name": "Hermione", "age": 13}, {"name": "Hagrid", "age": 50}]}
        self._assert_match(expected, received)

        received = {"name": "Harry", "friends": [{"name": "Hermione", "age": 13}]}
        message = "There's 1 fields that differ\n- friends: Received 1 items and it was expected to have 2 "
        self._assert_not_match(expected, received, message)

        received = {
            "name": "Harry",
            "friends": [
                {"name": "Hermione", "age": 13},
                {"name": "Hagrid", "age": 50},
                {"name": "Dumbledore", "age": 100},
            ],
        }
        message = "There's 1 fields that differ\n- friends: Received 3 items and it was expected to have 2 "
        self._assert_not_match(expected, received, message)

        received = {"name": "Harry", "friends": "potato"}
        message = (
            "There's 1 fields that differ\n"
            "- friends: Received `potato`, "
            "but expected to `[{'name': 'Hermione', 'age': 13}, {'name': 'Hagrid', 'age': 50}]` "
        )
        self._assert_not_match(expected, received, message)

    def test_match_set(self):
        expected = {"name": "Harry", "friends": {"Hermione", "Hagrid", "Dumbledore"}}

        received = {"name": "Harry", "friends": ["Hermione", "Hagrid", "Dumbledore"]}
        self._assert_match(expected, received)

        received = {"name": "Harry", "friends": ["Hagrid", "Hermione", "Dumbledore"]}
        self._assert_match(expected, received)

        received = {"name": "Harry", "friends": {"Hagrid", "Hermione", "Dumbledore"}}
        self._assert_match(expected, received)

        received = {"name": "Harry", "friends": ["Hagrid", "Hermione"]}
        message = (
            "There's 1 fields that differ\n"
            "- friends: Received `Hagrid, Hermione`, but expected to have `Dumbledore, Hagrid, Hermione` items "
        )
        self._assert_not_match(expected, received, message)

        received = {"name": "Harry", "friends": ["Hagrid", "Hermione", "Dumbledore", "Valdemort"]}
        message = (
            "There's 1 fields that differ\n"
            "- friends: Received `Dumbledore, Hagrid, Hermione, Valdemort`, "
            "but expected to have `Dumbledore, Hagrid, Hermione` items "
        )
        self._assert_not_match(expected, received, message)

        received = {"name": "Harry", "friends": 13}
        message = (
            "There's 1 fields that differ\n"
            "- friends: Received `13`, but expected to have `Dumbledore, Hagrid, Hermione` items "
        )
        self._assert_not_match(expected, received, message)

    def test_match_list(self):
        expected = {"name": "Harry", "friends": ["Hermione", "Hagrid", "Dumbledore"]}

        received = {"name": "Harry", "friends": ["Hermione", "Hagrid", "Dumbledore"]}
        self._assert_match(expected, received)

        received = {"name": "Harry", "friends": ["Hagrid", "Hermione", "Dumbledore"]}
        message = (
            "There's 2 fields that differ\n"
            "- friends.[#0] __eq__: Received `Hagrid`, but expected `Hermione` \n"
            "- friends.[#1] __eq__: Received `Hermione`, but expected `Hagrid` "
        )
        self._assert_not_match(expected, received, message)

        received = {"name": "Harry", "friends": ["Hagrid", "Hermione"]}
        message = "There's 1 fields that differ\n- friends: Received 2 items and it was expected to have 3 "
        self._assert_not_match(expected, received, message)

        received = {"name": "Harry", "friends": ["Hagrid", "Hermione", "Dumbledore", "Valdemort"]}
        message = "There's 1 fields that differ\n- friends: Received 4 items and it was expected to have 3 "
        self._assert_not_match(expected, received, message)

        received = {"name": "Harry", "friends": 13}
        message = (
            "There's 1 fields that differ\n"
            "- friends: Received `13`, but expected to `['Hermione', 'Hagrid', 'Dumbledore']` "
        )
        self._assert_not_match(expected, received, message)

    def test_match_error_types(self):
        expected = {"birthday": datetime(2022, 1, 1, 0, 0, 0, tzinfo=UTC)}
        received = {"birthday": "2022-01-01 00:00:00"}

        message = (
            "There's 1 fields that differ\n- birthday: Received `<class 'str'>`, "
            "but expected `<class 'datetime.datetime'>"
        )
        self._assert_not_match(expected, received, message)
