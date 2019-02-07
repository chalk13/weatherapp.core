import unittest
import io
import sys

from weatherapp.core.app import App


class CommandsTestCase(unittest.TestCase):
    """Test case for commands tests."""

    def test_providers(self):
        """Test providers command."""

        sys.stdout = io.StringIO()
        App(stdout=sys.stdout).run(['providers'])
        sys.stdout.seek(0)
        self.assertEqual(sys.stdout.read(), 'AccuWeather (accu)\nRP5 (rp5)\nSINOPTIK (sinoptik)\n')
