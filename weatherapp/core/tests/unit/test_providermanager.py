import unittest

from weatherapp.core.providermanager import ProviderManager


class ExampleCommand:
    pass


class ProviderManagerTestCase(unittest.TestCase):
    """Unit test case for provider manager."""

    def setUp(self):
        """Contain set up info for every single test."""
        self.provider_manager = ProviderManager()
        self.provider_manager.add('example', ExampleCommand)

    def test_load_providers(self):
        """Test _load_providers method for provider manager."""

        message = 'An error occurs during the _load_providers method.'
        self.assertTrue('accu' in self.provider_manager._providers, msg=message)
        self.assertTrue('rp5' in self.provider_manager._providers, msg=message)
        self.assertTrue('sinoptik' in self.provider_manager._providers, msg=message)

    def test_add(self):
        """Test add method for provider manager."""

        self.assertTrue('example' in self.provider_manager._providers,
                        msg="Command 'example' is missing in provider manager.")

    def test_get(self):
        """Test get method for provider manager."""

        self.assertEqual(self.provider_manager.get('example'), ExampleCommand)
        self.assertIsNone(self.provider_manager.get('bar'), ExampleCommand)

    def test_contains(self):
        """Test if '__contains__' method is working."""

        self.assertTrue('example' in self.provider_manager)
        self.assertFalse('bar' in self.provider_manager)

    def test_len(self):
        """Test if '__len__' method is working."""

        self.assertEqual(4, len(self.provider_manager._providers))


if __name__ == '__main__':
    unittest.main()
