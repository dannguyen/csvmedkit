import re

import csvmedkit
import csvmedkit.__about__ as about

from tests.mk import TestCase, skiptest

from csvmedkit.cmk.cmkutil import CmkUtil
from csvmedkit.cmk.helpers import cmk_parse_column_ids, cmk_parse_delimited_str


class TestCMK(TestCase):
    def test_about(self):
        self.assertEqual("csvmedkit", about.__title__)

    def test_version(self):
        assert re.match(r"\d+\.\d+\.\d+", about.__version__)

    def test_cmk_parse_column_ids(self):
        """probably redundant"""
        cols = ["a", "b", "c"]
        self.assertEqual(cmk_parse_column_ids("c,b,a,c", cols), [2, 1, 0, 2])
        self.assertEqual(cmk_parse_column_ids("2-3,1,1-3", cols), [1, 2, 0, 0, 1, 2])


class TestParseDelims(TestCase):
    def test_basic(self):
        txt = "hello,world"
        self.assertEqual(
            ["hello", "world"],
            cmk_parse_delimited_str(txt),
        )

    def test_empty_string(self):
        self.assertEqual([], cmk_parse_delimited_str(""))

    def test_custom_delim(self):
        txt = "hello|foo,bar|world"
        # positional
        self.assertEqual(
            ["hello", "foo,bar", "world"],
            cmk_parse_delimited_str(
                txt,
                "|",
            ),
        )

        # keyword
        self.assertEqual(
            ["hello", "foo,bar", "world"],
            cmk_parse_delimited_str(
                txt,
                delimiter="|",
            ),
        )

    def test_minlength_basic(self):
        txt = "hello,world"
        a, b, c = cmk_parse_delimited_str(txt, minlength=3)
        assert a == "hello"
        assert b == "world"
        assert c == ""

    def test_minlength_too_small(self):
        d = cmk_parse_delimited_str(
            "hello|foo,bar",
            "|",
            1,
        )
        assert d == ["hello", "foo,bar"]

    def test_minlength_too_big(self):
        d = cmk_parse_delimited_str(
            "hello",
            ",",
            3,
        )
        assert d == [
            "hello",
            "",
            "",
        ]

    def test_minlength_pads_empty_input(self):
        d = cmk_parse_delimited_str(
            "",
            ",",
            3,
        )
        assert d == [
            "",
            "",
            "",
        ]
