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
                "| ===== |       |",
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
                "| ===== |       |",
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
                    "| ===== |       |",
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
                "| ===== |       |",
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
                "| ===== |       |",
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
                "| ===== |       |",
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
                "| ===== |            |",
                "| code  | beta       |",
                "| blob  | ABCDEFGHIJ |",
            ],
        )


class TestSeparator(TestCSVFlatten):
    def test_custom(self):
        self.assertLines(
            ["-S", "My Custom Sep", "examples/dummy2.csv"],
            [
                "| field         | value |",
                "| ------------- | ----- |",
                "| a             | 1     |",
                "| b             | 2     |",
                "| c             | 3     |",
                "| My Custom Sep |       |",
                "| a             | 8     |",
                "| b             | 9     |",
                "| c             | 10    |",
            ],
        )

    def test_none(self):
        self.assertLines(
            ["--separator", "none", "examples/dummy2.csv"],
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

    def test_blank(self):
        self.assertLines(
            ["-S", "", "examples/dummy2.csv"],
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

    def test_newline(self):
        answer = [
            "| field | value |",
            "| ----- | ----- |",
            "| a     | 1     |",
            "| b     | 2     |",
            "| c     | 3     |",
            "|       |       |",
            "| a     | 8     |",
            "| b     | 9     |",
            "| c     | 10    |",
        ]

        self.assertLines(["-N", "examples/dummy2.csv"], list(answer))
        self.assertLines(["--newline-sep", "examples/dummy2.csv"], list(answer))

    def test_error_if_newline_and_custom_separator(self):
        ioerr = StringIO()
        with contextlib.redirect_stderr(ioerr):
            with self.assertRaises(SystemExit) as e:
                u = self.get_output(["-N", "-S", "x", "examples/dummy.csv"])
        self.assertEqual(e.exception.code, 2)
        self.assertIn(
            "Cannot set both -N/--newline-sep and -S/--separator", ioerr.getvalue()
        )


class TestMaxLength(TestCSVFlatten):
    def test_default(self):
        iof = StringIO("a,b,c\n0,12345,67890\n")
        with stdin_as_string(iof):
            self.assertLines(
                ["--max-length", "3"],
                [
                    "| field | value |",
                    "| ----- | ----- |",
                    "| a     | 0     |",
                    "| b     | 123   |",
                    "|       | 45    |",
                    "| c     | 678   |",
                    "|       | 90    |",
                ],
            )

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
                "| ===== |       |",
                "| a     | 8     |",
                "| b     | 9     |",
                "| c     | 10    |",
            ],
        )


class TestRecIds(TestCSVFlatten):
    def test_default(self):
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

    def test_with_separator(self):
        self.assertLines(
            ["-R", "-S", "xyz", "examples/dummy2.csv"],
            [
                "| recid | field | value |",
                "| ----- | ----- | ----- |",
                "|     0 | a     | 1     |",
                "|     0 | b     | 2     |",
                "|     0 | c     | 3     |",
                "|       | xyz   |       |",
                "|     1 | a     | 8     |",
                "|     1 | b     | 9     |",
                "|     1 | c     | 10    |",
            ],
        )

    def test_with_newline_separator(self):
        self.assertLines(
            ["-R", "-N", "examples/dummy2.csv"],
            [
                "| recid | field | value |",
                "| ----- | ----- | ----- |",
                "|     0 | a     | 1     |",
                "|     0 | b     | 2     |",
                "|     0 | c     | 3     |",
                "|       |       |       |",
                "|     1 | a     | 8     |",
                "|     1 | b     | 9     |",
                "|     1 | c     | 10    |",
            ],
        )


class TestChunkLabel(TestCSVFlatten):

    #########################################
    ## chop/chunk label
    ##########################################

    def test_label_chunks_basic(self):
        """
        Even without -L set, multilines values are split into different records.

        Note that unlike prior versions, -B/--label-chunks can be set without -L
        """
        self.assertLines(
            [
                "examples/dummy2m.csv",
                "-B",
            ],
            [
                "| field | value |",
                "| ----- | ----- |",
                "| a     | 1     |",
                "| b     | 2     |",
                "| c     | 3, 4  |",
                "| ===== |       |",
                "| a     | 8     |",
                "| b     | 9     |",
                "| c     | 10    |",
            ],
        )

    def test_label_chunks_and_max_length(self):
        """
        --label-chunks adds label to every chunk

        Note that default record separator doesn't quite
            match max-column-width...oh well
        """
        eor = "====="
        self.assertLines(
            ["examples/statecodes.csv", "-L", "5", "--label-chunks"],
            [
                "| field   | value |",
                "| ------- | ----- |",
                "| code    | IA    |",
                "| name    | Iowa  |",
                "| =====   |       |",
                "| code    | RI    |",
                "| name    | Rhode |",
                "| name__1 | Islan |",
                "| name__2 | d     |",
                "| =====   |       |",
                "| code    | TN    |",
                "| name    | Tenne |",
                "| name__1 | ssee  |",
            ],
        )
