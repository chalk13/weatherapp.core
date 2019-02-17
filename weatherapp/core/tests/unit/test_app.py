"""Unittests for App class"""

import argparse
import unittest

from weatherapp.core.app import App


class AppTestCase(unittest.TestCase):
    """Test application class methods."""

    def setUp(self):
        """Contain set up info for every single test."""
        self.parser = App._arg_parse()
        self.formatter = App._load_formatters()

    def test_arg_parser(self):
        """Test application argument parser creation."""

        self.assertIsInstance(self.parser, argparse.ArgumentParser)

    def test_arg_parser_default_values(self):
        """Test application argument parser default values."""

        parsed_args = self.parser.parse_args([])
        self.assertIsNone(parsed_args.command)
        self.assertFalse(parsed_args.debug)
        self.assertEqual(parsed_args.formatter, 'table')

    def test_arg_parser_arg(self):
        """Test application argument parser"""

        parsed_args = self.parser.parse_args(['accu', '--debug', '--refresh', '-v'])
        self.assertEqual(parsed_args.command, 'accu')
        self.assertTrue(parsed_args.debug)
        self.assertEqual(parsed_args.formatter, 'table')
        self.assertTrue(parsed_args.refresh)
        self.assertEqual(parsed_args.verbose_level, 1)

    def test_load_formatters(self):
        """Test application formatter loading"""

        self.assertTrue(self.formatter)
        self.assertIsInstance(self.formatter, dict)


if __name__ == '__main__':
    unittest.main()
