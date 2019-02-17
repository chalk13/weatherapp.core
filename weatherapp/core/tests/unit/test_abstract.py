"""Unit tests for abstract classes."""

import unittest
from unittest.mock import patch

from weatherapp.core.abstract import Formatter, Manager


class FormatterTestCase(unittest.TestCase):
    """Unit test case for formatter abstract class"""

    @patch.multiple(Formatter, __abstractmethods__=set())
    def test(self):
        self.instance = Formatter()


class ManagerTestCase(unittest.TestCase):
    """Unit test case for manager abstract class"""

    @patch.multiple(Manager, __abstractmethods__=set())
    def test(self):
        self.instance = Manager()


if __name__ == '__main__':
    unittest.main()
