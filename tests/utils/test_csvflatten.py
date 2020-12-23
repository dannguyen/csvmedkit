from collections import namedtuple
import contextlib
from io import StringIO
from unittest.mock import patch
import sys


from csvmedkit.exceptions import *
from csvmedkit.utils.csvflatten import (
    CSVFlatten,
    launch_new_instance,
    DEFAULT_EOR_MARKER,
)

from tests.mk import CmkTestCase, EmptyFileTests, stdin_as_string, skiptest


class TestCSVFlatten(CmkTestCase, EmptyFileTests):
    Utility = CSVFlatten


class TestInit(TestCSVFlatten, EmptyFileTests):
    def test_launch_new_instance(self):
        with patch.object(
            sys, "argv", [self.Utility.__name__.lower(), "examples/dummy.csv"]
        ):
            launch_new_instance()

    def test_basic(self):
        """
        default operation is to transpose the table into field,value form
        """
        self.assertLines(
            ["examples/dummy.csv"],
            [
                "| field | value |",
                "| ----- | ----- |",
                "| a     | 1     |",
                "| b     | 2     |",
                "| c     | 3     |",
            ],
        )

    def test_skip_lines(self):
        self.assertLines(
            ["--skip-lines", "3", "examples/test_skip_lines.csv"],
            [
                "| field | value |",
                "| ----- | ----- |",
                "| a     | 1     |",
                "| b     | 2     |",
                "| c     | 3     |",
            ],
        )

    def test_basic_mutli_records(self):
        self.assertLines(
            ["examples/dummy2.csv"],
            [
                "| field | value |",
                "| ----- | ----- |",
                "| a     | 1     |",
                "| b     | 2     |",
                "| c     | 3     |",
                "| ~~~~~ |       |",
                "| a     | 8     |",
                "| b     | 9     |",
                "| c     | 10    |",
            ],
        )

    def test_basic_multiline(self):
        """even without -L set, multilines are split into different records"""
        self.assertLines(
            ["examples/dummy2m.csv"],
            [
                "| field | value |",
                "| ----- | ----- |",
                "| a     | 1     |",
                "| b     | 2     |",
                "| c     | 3, 4  |",
                "| ~~~~~ |       |",
                "| a     | 8     |",
                "| b     | 9     |",
                "| c     | 10    |",
            ],
        )

    def test_blank_columns(self):
        input_file = StringIO("a,b,c\n1,,3\n,,\n")
        with stdin_as_string(input_file):
            self.assertLines(
                [],
                [
                    "| field | value |",
                    "| ----- | ----- |",
                    "| a     | 1     |",
                    "| b     |       |",
                    "| c     | 3     |",
                    "| ~~~~~ |       |",
                    "| a     |       |",
                    "| b     |       |",
                    "| c     |       |",
                ],
            )


class TestDefaultPrettify(TestCSVFlatten):
    def test_prettify_basic(self):
        self.assertLines(
            ["examples/dummy.csv"],
            [
                "| field | value |",
                "| ----- | ----- |",
                "| a     | 1     |",
                "| b     | 2     |",
                "| c     | 3     |",
            ],
        )

    def test_prettify_basic_n_records(self):
        self.assertLines(
            ["examples/dummy2.csv"],
            [
                "| field | value |",
                "| ----- | ----- |",
                "| a     | 1     |",
                "| b     | 2     |",
                "| c     | 3     |",
                "| ~~~~~ |       |",
                "| a     | 8     |",
                "| b     | 9     |",
                "| c     | 10    |",
            ],
        )

    def test_prettify_multiline_records(self):
        """
        By default, newlines are converted to simple whitespace via textwrap.wrap(); note that this is
        a result of --prettify setting --max-length by default

        """
        self.assertLines(
            ["examples/dummy2m.csv"],
            [
                "| field | value |",
                "| ----- | ----- |",
                "| a     | 1     |",
                "| b     | 2     |",
                "| c     | 3, 4  |",
                "| ~~~~~ |       |",
                "| a     | 8     |",
                "| b     | 9     |",
                "| c     | 10    |",
            ],
        )

    @patch("csvmedkit.utils.csvflatten.get_terminal_size")
    def test_prettify_uses_terminal_size_by_default(self, mock_get_tsize):
        Tz = namedtuple("terminal_size", ["columns", "lines"])
        mock_get_tsize.return_value = Tz(23, 42)
        lines = self.assertLines(
            [
                "examples/abc123.csv",
            ],
            [
                "| field | value |",
                "| ----- | ----- |",
                "| code  | alfa  |",
                "| blob  | 01234 |",
                "|       | 56789 |",
                "| ~~~~~ |       |",
                "| code  | beta  |",
                "| blob  | ABCDE |",
                "|       | FGHIJ |",
            ],
        )

    @patch("csvmedkit.utils.csvflatten.get_terminal_size")
    def test_prettify_ignores_terminal_size_if_too_small(self, mock_get_tsize):
        """
        if the calculated field widths are wider than the terminal (by the margin of a padding value),
        then DEFAULT_MAX_WIDTH is used for the .max_field_length
        """
        Tz = namedtuple("terminal_size", ["columns", "lines"])
        mock_get_tsize.return_value = Tz(15, 42)
        lines = self.assertLines(
            [
                "examples/abc123.csv",
            ],
            [
                "| field | value      |",
                "| ----- | ---------- |",
                "| code  | alfa       |",
                "| blob  | 0123456789 |",
                "| ~~~~~ |            |",
                "| code  | beta       |",
                "| blob  | ABCDEFGHIJ |",
            ],
        )


class TestPrettifyCombo(TestCSVFlatten):
    """test prettify with other settings to make make sure side-effects don't conflict"""

    def test_prettify_multiline_records_disable_max_length(self):
        """newlines NOT converted to whitespace if we disable max chop length"""
        self.assertLines(
            ["-L", "0", "examples/dummy2m.csv"],
            [
                "| field | value |",
                "| ----- | ----- |",
                "| a     | 1     |",
                "| b     | 2     |",
                "| c     | 3,    |",
                "|       | 4     |",
                "| ~~~~~ |       |",
                "| a     | 8     |",
                "| b     | 9     |",
                "| c     | 10    |",
            ],
        )

    def test_prettify_eor_none(self):
        self.assertLines(
            ["-E", "none", "examples/dummy2.csv"],
            [
                "| field | value |",
                "| ----- | ----- |",
                "| a     | 1     |",
                "| b     | 2     |",
                "| c     | 3     |",
                "| a     | 8     |",
                "| b     | 9     |",
                "| c     | 10    |",
            ],
        )

    def test_prettify_rec_ids(self):
        self.assertLines(
            ["--rec-id", "examples/dummy2.csv"],
            [
                "| recid | field | value |",
                "| ----- | ----- | ----- |",
                "|     0 | a     | 1     |",
                "|     0 | b     | 2     |",
                "|     0 | c     | 3     |",
                "|     1 | a     | 8     |",
                "|     1 | b     | 9     |",
                "|     1 | c     | 10    |",
            ],
        )
