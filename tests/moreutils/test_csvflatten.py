from collections import namedtuple
import contextlib
from io import StringIO
from unittest.mock import patch
from unittest import skip as skiptest
import sys


from csvmedkit.exceptions import *
from csvmedkit.moreutils.csvflatten import (
    CSVFlatten,
    launch_new_instance,
    DEFAULT_EOR_MARKER,
)
from tests.tk import CSVKitTestCase, EmptyFileTests, stdin_as_string


class TestCSVFlatten(CSVKitTestCase, EmptyFileTests):
    Utility = CSVFlatten

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
                "field,value",
                "a,1",
                "b,2",
                "c,3",
            ],
        )

    def test_skip_lines(self):
        self.assertLines(
            ["--skip-lines", "3", "examples/test_skip_lines.csv"],
            [
                "field,value",
                "a,1",
                "b,2",
                "c,3",
            ],
        )

    def test_basic_mutli_records(self):
        self.assertLines(
            ["examples/dummy2.csv"],
            [
                "field,value",
                "a,1",
                "b,2",
                "c,3",
                "~~~~~,",
                "a,8",
                "b,9",
                "c,10",
            ],
        )

    def test_basic_multiline(self):
        """even without -L set, multilines are split into different records"""
        self.assertLines(
            ["examples/dummy2m.csv"],
            [
                "field,value",
                "a,1",
                "b,2",
                'c,"3,"',
                ",4",
                "~~~~~,",
                "a,8",
                "b,9",
                "c,10",
            ],
        )

    def test_blank_columns(self):
        input_file = StringIO("a,b,c\n1,,3\n,,\n")
        with stdin_as_string(input_file):
            self.assertLines(
                [],
                [
                    "field,value",
                    "a,1",
                    "b,",
                    "c,3",
                    "~~~~~,",
                    "a,",
                    "b,",
                    "c,",
                ],
            )

        input_file.close()

    #########################################
    ## cmax length
    ##########################################

    def test_max_length(self):
        self.assertLines(
            ["examples/statecodes.csv", "-L", "5"],
            [
                "field,value",
                "code,IA",
                "name,Iowa",
                f"~~~~~,",
                "code,RI",
                "name,Rhode",
                ",Islan",
                ",d",
                f"~~~~~,",
                "code,TN",
                "name,Tenne",
                ",ssee",
            ],
        )

    #########################################
    ## chop/chunk label
    ##########################################

    def test_chunk_label_basic(self):
        """
        Even without -L set, multilines values are split into different records.

        Note that unlike prior versions, -B/--chunk-labels can be set without -L
        """
        self.assertLines(
            [
                "examples/dummy2m.csv",
                "-B",
            ],
            [
                "field,value",
                "a,1",
                "b,2",
                'c,"3,"',
                "c__1,4",
                "~~~~~,",
                "a,8",
                "b,9",
                "c,10",
            ],
        )

    def test_chunk_label_and_max_length(self):
        """
        --chunk-labels adds label to every chunk
        """
        eor = "~~~~~"
        self.assertLines(
            ["examples/statecodes.csv", "--max-length", "5", "--chunk-labels"],
            [
                "field,value",
                "code,IA",
                "name,Iowa",
                f"{eor},",
                "code,RI",
                "name,Rhode",
                "name__1,Islan",
                "name__2,d",
                f"{eor},",
                "code,TN",
                "name,Tenne",
                "name__1,ssee",
            ],
        )

        """same test, but with alt label"""
        self.assertLines(
            ["examples/statecodes.csv", "-L", "5", "-B"],
            [
                "field,value",
                "code,IA",
                "name,Iowa",
                f"{eor},",
                "code,RI",
                "name,Rhode",
                "name__1,Islan",
                "name__2,d",
                f"{eor},",
                "code,TN",
                "name,Tenne",
                "name__1,ssee",
            ],
        )

    #########################################
    ## end of record marker/separator
    ##########################################

    def test_end_of_record_marker_default(self):
        """
        alpha,omega
        1,9
        a,z
        $,%
        """
        eor = "".join(
            DEFAULT_EOR_MARKER for i in range(max(len(j) for j in ("alpha", "omega")))
        )
        self.assertLines(
            [
                "examples/tinyvals.csv",
            ],
            [
                """field,value""",
                """alpha,1""",
                """omega,9""",
                f"""{eor},""",
                """alpha,a""",
                """omega,z""",
                f"""{eor},""",
                """alpha,$""",
                """omega,%""",
            ],
        )

    def test_no_end_of_record_marker(self):
        self.assertLines(
            ["examples/tinyvals.csv", "--eor", ""],
            [
                """field,value""",
                """alpha,1""",
                """omega,9""",
                """alpha,a""",
                """omega,z""",
                """alpha,$""",
                """omega,%""",
            ],
        )
        self.assertLines(
            ["examples/tinyvals.csv", "-E", "none"],
            [
                """field,value""",
                """alpha,1""",
                """omega,9""",
                """alpha,a""",
                """omega,z""",
                """alpha,$""",
                """omega,%""",
            ],
        )

    def test_custom_end_of_record_marker(self):
        self.assertLines(
            ["examples/tinyvals.csv", "-E", "False"],
            [
                """field,value""",
                """alpha,1""",
                """omega,9""",
                f"""False,""",
                """alpha,a""",
                """omega,z""",
                f"""False,""",
                """alpha,$""",
                """omega,%""",
            ],
        )

        # all-caps NONE is NOT treated as "none"
        self.assertLines(
            ["examples/tinyvals.csv", "-E", "NONE"],
            [
                """field,value""",
                """alpha,1""",
                """omega,9""",
                f"""NONE,""",
                """alpha,a""",
                """omega,z""",
                f"""NONE,""",
                """alpha,$""",
                """omega,%""",
            ],
        )

    ###################################################################################################
    # row_id mode
    ###################################################################################################

    def test_row_id_basic(self):
        """
        prepend recid column; by default, --E/--eor is disabled
        """
        self.assertLines(
            ["-R", "examples/dummy2.csv"],
            [
                "recid,field,value",
                "0,a,1",
                "0,b,2",
                "0,c,3",
                "1,a,8",
                "1,b,9",
                "1,c,10",
            ],
        )

    def test_row_id_eor(self):
        """
        user has option to add -E/--eor if they want
        """
        self.assertLines(
            ["--rec-id", "-E", "WOAH", "examples/dummy2.csv"],
            [
                "recid,field,value",
                "0,a,1",
                "0,b,2",
                "0,c,3",
                ",WOAH,",
                "1,a,8",
                "1,b,9",
                "1,c,10",
            ],
        )

    def test_row_id_multiline(self):
        """for multiline vals that are now multirows, rec_id will have a value, even if field is blank"""
        self.assertLines(
            ["-R", "examples/dummy2m.csv"],
            [
                "recid,field,value",
                "0,a,1",
                "0,b,2",
                '0,c,"3,"',
                "0,,4",
                "1,a,8",
                "1,b,9",
                "1,c,10",
            ],
        )

    ###################################################################################################
    # prettify mode
    ###################################################################################################

    def test_prettify_basic(self):
        self.assertLines(
            ["-P", "examples/dummy.csv"],
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
            ["--prettify", "examples/dummy2.csv"],
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
            ["-P", "examples/dummy2m.csv"],
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

    @patch("csvmedkit.moreutils.csvflatten.get_terminal_size")
    def test_prettify_uses_terminal_size_by_default(self, mock_get_tsize):
        Tz = namedtuple("terminal_size", ["columns", "lines"])
        mock_get_tsize.return_value = Tz(23, 42)
        lines = self.assertLines(
            [
                "-P",
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

    @patch("csvmedkit.moreutils.csvflatten.get_terminal_size")
    def test_prettify_ignores_terminal_size_if_too_small(self, mock_get_tsize):
        """
        if the calculated field widths are wider than the terminal (by the margin of a padding value),
        then DEFAULT_MAX_WIDTH is used for the .max_field_length
        """
        Tz = namedtuple("terminal_size", ["columns", "lines"])
        mock_get_tsize.return_value = Tz(15, 42)
        lines = self.assertLines(
            [
                "-P",
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

    def test_prettify_multiline_records_disable_max_length(self):
        """newlines NOT converted to whitespace if we disable max chop length"""
        self.assertLines(
            ["-P", "-L", "0", "examples/dummy2m.csv"],
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
            ["-P", "-E", "none", "examples/dummy2.csv"],
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
            ["-P", "--rec-id", "examples/dummy2.csv"],
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

    ###################################################################################################
    ### Tests that verify my examples
    ###################################################################################################
    @skiptest("write out examples later")
    def test_regular_hamlet_w_csvlook(self):
        self.assertLines(["examples/hamlet.csv", "-P"], ["lines"])

    ################################
    # obsolete
    ################################

    @skiptest("obsolete: no longer need to force this")
    def test_forced_quoting_in_max_length_mode(self):
        self.assertLines(
            [
                "examples/dummy.csv",
                "--max-length",
                "42",
            ],
            [
                '"field","value"',
                '"a","1"',
                '"b","2"',
                '"c","3"',
            ],
        )
        self.assertLines(
            [
                "examples/dummy.csv",
                "-L",
                "42",
            ],
            [
                '"field","value"',
                '"a","1"',
                '"b","2"',
                '"c","3"',
            ],
        )
