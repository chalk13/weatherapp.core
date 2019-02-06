import unittest

from weatherapp.core.commandmanager import CommandManager


class ExampleCommand:
    pass


class CommandManagerTestCase(unittest.TestCase):
    """Unit test case for command manager."""

    def setUp(self):
        self.command_manager = CommandManager()

    def test_add(self):
        """Test add method for command manager."""

        self.command_manager.add('example', ExampleCommand)

        self.assertTrue('example' in self.command_manager._commands,
                        msg="Command 'example' is missing in command manager.")

    def test_get(self):
        """Test get method for command manager."""

        self.command_manager.add('example', ExampleCommand)

        self.assertEqual(self.command_manager.get('example'), ExampleCommand)
        self.assertIsNone(self.command_manager.get('bar'), ExampleCommand)

    def test_contains(self):
        """Test if '__contains__' method is working."""

        self.command_manager.add('example', ExampleCommand)

        self.assertTrue('example' in self.command_manager)
        self.assertFalse('bar' in self.command_manager)


if __name__ == '__main__':
    unittest.main()
