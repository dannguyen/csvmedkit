import unittest
from unittest import skip as skiptest

import re

import csvmedkit
import csvmedkit.__about__ as about

from csvmedkit.cmkutil import CmkUtil, cmk_parse_column_ids


class TestCMK(unittest.TestCase):
    def test_about(self):
        self.assertEqual("csvmedkit", about.__title__)

    def test_version(self):
        assert re.match(r"\d+\.\d+\.\d+", about.__version__)

    def test_cmk_parse_column_ids(self):
        """probably redundant"""
        cols = ["a", "b", "c"]
        self.assertEqual(cmk_parse_column_ids("c,b,a,c", cols), [2, 1, 0, 2])
        self.assertEqual(cmk_parse_column_ids("2-3,1,1-3", cols), [1, 2, 0, 0, 1, 2])
