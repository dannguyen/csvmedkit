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
            ["--csv", "examples/dummy.csv"],
            [
                "field,value",
                "a,1",
                "b,2",
                "c,3",
            ],
        )

    def test_skip_lines(self):
        self.assertLines(
            ["--skip-lines", "3", "-c", "examples/test_skip_lines.csv"],
            [
                "field,value",
                "a,1",
                "b,2",
                "c,3",
            ],
        )

    def test_basic_mutli_records(self):
        self.assertLines(
            ["-c", "examples/dummy2.csv"],
            [
                "field,value",
                "a,1",
                "b,2",
                "c,3",
                "=====,",
                "a,8",
                "b,9",
                "c,10",
            ],
        )

    def test_basic_multiline(self):
        """even without -L set, multilines are split into different records"""
        self.assertLines(
            ["-c", "examples/dummy2m.csv"],
            [
                "field,value",
                "a,1",
                "b,2",
                'c,"3,"',
                ",4",
                "=====,",
                "a,8",
                "b,9",
                "c,10",
            ],
        )

    def test_blank_columns(self):
        input_file = StringIO("a,b,c\n1,,3\n,,\n")
        with stdin_as_string(input_file):
            self.assertLines(
                ["-c"],
                [
                    "field,value",
                    "a,1",
                    "b,",
                    "c,3",
                    "=====,",
                    "a,",
                    "b,",
                    "c,",
                ],
            )

        input_file.close()


class TestMaxLength(TestCSVFlatten):
    #########################################
    ## cmax length
    ##########################################

    def test_max_length(self):
        self.assertLines(
            ["-c", "examples/statecodes.csv", "-L", "5"],
            [
                "field,value",
                "code,IA",
                "name,Iowa",
                f"=====,",
                "code,RI",
                "name,Rhode",
                ",Islan",
                ",d",
                f"=====,",
                "code,TN",
                "name,Tenne",
                ",ssee",
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
                "-c",
                "examples/dummy2m.csv",
                "-B",
            ],
            [
                "field,value",
                "a,1",
                "b,2",
                'c,"3,"',
                "c__1,4",
                "=====,",
                "a,8",
                "b,9",
                "c,10",
            ],
        )

    def test_label_chunks_and_max_length(self):
        """
        --label-chunks adds label to every chunk
        """
        eor = "====="
        self.assertLines(
            ["-c", "examples/statecodes.csv", "--max-length", "5", "--label-chunks"],
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
            ["-c", "examples/statecodes.csv", "-L", "5", "-B"],
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


class TestEor(TestCSVFlatten):

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
                "-c",
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
            ["-c", "examples/tinyvals.csv", "--separator", ""],
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
            ["-c", "examples/tinyvals.csv", "-S", "none"],
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
            ["-c", "examples/tinyvals.csv", "-S", "False"],
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
            ["-c", "examples/tinyvals.csv", "-S", "NONE"],
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


class TestRowId(TestCSVFlatten):

    ###################################################################################################
    # row_id mode
    ###################################################################################################

    def test_row_id_basic(self):
        """
        prepend recid column; by default, --S/--separator is disabled
        """
        self.assertLines(
            ["-R", "-c", "examples/dummy2.csv"],
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
        user has option to add -S/--separator if they want
        """
        self.assertLines(
            ["--rec-id", "-S", "WOAH", "-c", "examples/dummy2.csv"],
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
            ["-R", "-c", "examples/dummy2m.csv"],
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


class TestPrettifyCombo(TestCSVFlatten):
    """
    tklegacy
    test prettify with other settings to make make sure side-effects don't conflict

    legacy tests from before non-default-prettify
    """

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

    def test_prettify_eor_none(self):
        self.assertLines(
            ["-S", "none", "examples/dummy2.csv"],
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


################################
# obsolete
################################
@skiptest("obsolete: no longer need to force this")
def test_forced_quoting_in_max_length_mode(self):
    self.assertLines(
        [
            "-c",
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
            "-c",
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


# ###################################################################################################
# ### Tests that verify my documentation examples
# ###################################################################################################
# class TestDocExamples(TestCSVFlatten):
#     """Tests that verify my documentation examples"""

#     @skiptest("write out examples later")
#     def test_intro(self):
#         pass

#     @skiptest("write out examples later")
#     def test_regular_hamlet_w_csvlook(self):
#         self.assertLines(["-c", "examples/hamlet.csv",], ["lines"])
