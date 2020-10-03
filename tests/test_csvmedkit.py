import unittest
from unittest import skip as skiptest

import re

import csvmedkit
import csvmedkit.__about__ as about


class FunTestCase(unittest.TestCase):
    def test_about(self):
        self.assertEqual("csvmedkit", about.__title__)

    def test_version(self):
        assert re.match(r"\d+\.\d+\.\d+", about.__version__)
