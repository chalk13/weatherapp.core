"""Unittests for Command manager class."""

import unittest

from weatherapp.core.commandmanager import CommandManager


class ExampleCommand:
    """Test class"""
    pass


class CommandManagerTestCase(unittest.TestCase):
    """Unit test case for command manager."""

    def setUp(self):
        """Contain set up info for every single test."""
        self.command_manager = CommandManager()
        self.command_manager.add('example', ExampleCommand)

    def test_add(self):
        """Test add method for command manager."""

        self.assertTrue('example' in self.command_manager._commands,
                        msg="Command 'example' is missing in command manager.")

    def test_load_commands(self):
        """Test _load_commands method for command manager."""

        message = 'An error occurs during the _load_commands method.'
        self.assertTrue('config' in self.command_manager._commands, msg=message)
        self.assertTrue('providers' in self.command_manager._commands, msg=message)

    def test_get(self):
        """Test get method for command manager."""

        self.assertEqual(self.command_manager.get('example'), ExampleCommand)
        self.assertIsNone(self.command_manager.get('bar'), ExampleCommand)

    def test_contains(self):
        """Test if '__contains__' method is working."""

        self.assertTrue('example' in self.command_manager)
        self.assertFalse('bar' in self.command_manager)


if __name__ == '__main__':
    unittest.main()
