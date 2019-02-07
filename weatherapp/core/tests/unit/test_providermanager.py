import unittest

from weatherapp.core.providermanager import ProviderManager


class ExampleCommand:
    pass


class ProviderManagerTestCase(unittest.TestCase):
    """Unit test case for provider manager."""

    def setUp(self):
        """Contain set up info for every single test."""
        self.provider_manager = ProviderManager()

    def test_add(self):
        """Test add method for provider manager."""

        self.provider_manager.add('example', ExampleCommand)

        self.assertTrue('example' in self.provider_manager._providers,
                        msg="Command 'example' is missing in provider manager.")

    def test_get(self):
        """Test get method for provider manager."""

        self.provider_manager.add('example', ExampleCommand)

        self.assertEqual(self.provider_manager.get('example'), ExampleCommand)
        self.assertIsNone(self.provider_manager.get('bar'), ExampleCommand)

    def test_contains(self):
        """Test if '__contains__' method is working."""

        self.provider_manager.add('example', ExampleCommand)

        self.assertTrue('example' in self.provider_manager)
        self.assertFalse('bar' in self.provider_manager)


if __name__ == '__main__':
    unittest.main()
