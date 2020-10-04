from unittest.mock import patch
from unittest import skip as skiptest
import sys


from csvmedkit.exceptions import *
from csvmedkit.moreutils.csvflatten import (
    CSVFlatten,
    launch_new_instance,
    DEFAULT_EOR_MARKER,
)
from tests.utils import CSVKitTestCase, EmptyFileTests


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

    def test_forced_quoting_in_chop_length_mode(self):
        self.assertLines(
            [
                "examples/dummy.csv",
                "--chop-length",
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

    def test_x_chop(self):
        self.assertLines(
            ["examples/statecodes.csv", "-L", "5"],
            [
                '"field","value"',
                '"code","IA"',
                '"name","Iowa"',
                f'"~~~~",""',
                '"code","RI"',
                '"name","Rhode"',
                '""," Isla"',
                '"","nd"',
                f'"~~~~",""',
                '"code","TN"',
                '"name","Tenne"',
                '"","ssee"',
            ],
        )

    def test_x_chop_field_label(self):
        """
        --chop-labels adds label to every chunk
        """
        eor = "~~~~"
        self.assertLines(
            ["examples/statecodes.csv", "-L", "5", "--chop-labels"],
            [
                '"field","value"',
                '"code","IA"',
                '"name","Iowa"',
                f'"{eor}",""',
                '"code","RI"',
                '"name","Rhode"',
                '"name__1"," Isla"',
                '"name__2","nd"',
                f'"{eor}",""',
                '"code","TN"',
                '"name","Tenne"',
                '"name__1","ssee"',
            ],
        )

        """same test, but with alt label"""
        self.assertLines(
            ["examples/statecodes.csv", "-L", "5", "-B"],
            [
                '"field","value"',
                '"code","IA"',
                '"name","Iowa"',
                f'"{eor}",""',
                '"code","RI"',
                '"name","Rhode"',
                '"name__1"," Isla"',
                '"name__2","nd"',
                f'"{eor}",""',
                '"code","TN"',
                '"name","Tenne"',
                '"name__1","ssee"',
            ],
        )

    ## end of record marker/separator
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

    @skiptest(
        "figure out how to set/patch terminal size for test; come up with fixtures file"
    )
    def test_prettify(self):
        pass

    ###################################################################################################
    ### Tests that verify my examples
    ###################################################################################################
    @skiptest("write out examples later")
    def test_regular_hamlet_w_csvlook(self):
        self.assertLines(["examples/hamlet.csv", "-P"], ["lines"])
