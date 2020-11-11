import contextlib
from io import StringIO
from subprocess import Popen, PIPE
import sys

from tests.mk import (
    CmkTestCase,
    ColumnsTests,
    EmptyFileTests,
    stdin_as_string,
    patch,
    parameterized,
    skiptest,
)

from csvmedkit.exceptions import ColumnIdentifierError
from csvmedkit.utils.csvsed import CSVSed, launch_new_instance


class TestCSVSed(CmkTestCase):
    Utility = CSVSed
    default_args = ["hello", "world"]
    columns_args = [
        "x",
        "y",
    ]


class TestInit(TestCSVSed, ColumnsTests, EmptyFileTests):
    def test_launch_new_instance(self):
        with patch.object(
            sys,
            "argv",
            [self.Utility.__name__.lower(), *self.default_args, "examples/dummy.csv"],
        ):
            launch_new_instance()

    def test_basic_dummy(self):
        """
        Shouldn't alter headers
        """
        self.assertLines(
            [r"(\w)", r"\1!", "examples/dummy.csv"],
            [
                "a,b,c",
                "1!,2!,3!",
            ],
        )

    def test_skip_lines(self):
        """redundant"""
        self.assertLines(
            [
                "--skip-lines",
                "3",
                r"\w",
                "x",
                "examples/test_skip_lines.csv",
            ],
            [
                "a,b,c",
                "x,x,x",
            ],
        )

    def test_basic_dummy_with_columns_arg(self):
        self.assertLines(
            ["-c", "1-3", r"(\w)", r"\1!", "examples/dummy.csv"],
            [
                "a,b,c",
                "1!,2!,3!",
            ],
        )


class TestRegexing(TestCSVSed):
    @property
    def idata(self):
        rows = ["id,name,val", "1,2,3x", "3,4,5", "6,7y,8z"]
        return StringIO("\n".join(rows))

    def test_captured_groups(self):
        with stdin_as_string(self.idata):
            self.assertLines(
                ["([a-z])", r"&\1&"],
                ["id,name,val", "1,2,3&x&", "3,4,5", "6,7&y&,8&z&"],
            )

    def test_named_groups(self):
        with stdin_as_string(self.idata):
            self.assertLines(
                [r"(?P<code>\d)(?P<sign>[a-z])", r"\g<sign>-\g<code>"],
                ["id,name,val", "1,2,x-3", "3,4,5", "6,y-7,z-8"],
            )

    def test_supports_case_insensitivity(self):
        tdata = "\n".join(["a,b,c,d", "hey,Hello,hat,hEx"])

        with stdin_as_string(StringIO(tdata)):
            self.assertLines(
                [
                    "(?i)h(?=e)",
                    "M",
                ],
                [
                    "a,b,c,d",
                    "Mey,Mello,hat,MEx",
                ],
            )

    def test_supports_case_insensitivity_obsolete(self):
        """maybe kill this test and its brittle example fixture?"""
        self.assertLines(
            [r"(?i)miss", "Ms.", "examples/honorifics-fem.csv"],
            [
                "code,name",
                "1,Mrs. Smith",
                "2,Ms. Daisy",
                "3,Ms. Doe",
                "4,Mrs Miller",
                "5,Ms Lee",
                "6,Ms. maam",
            ],
        )


class TestLiteralMatch(TestCSVSed):
    def test_literal_match(self):
        self.assertLines(
            ["-m", "s.", "x.", "examples/honorifics-fem.csv"],
            [
                "code,name",
                "1,Mrx. Smith",
                "2,Miss Daisy",
                "3,Mx. Doe",
                "4,Mrs Miller",
                "5,Ms Lee",
                "6,miss maam",
            ],
        )


class TestFilter(TestCSVSed):
    def test_default_without_filter_mode(self):
        """
        like basic sed, shouldn't be filtering out lines that don't match for replacement
        """
        self.assertLines(
            [r"([a-z])", r"\1!", "examples/tinyvals.csv"],
            [
                "alpha,omega",
                "1,9",
                "a!,z!",
                "$,%",
            ],
        )

    def test_filter_basic(self):
        """
        like-grep mode filters, then the sed is applied
        """
        self.assertLines(
            ["--filter", "4", "x", "examples/dummy5.csv"],
            [
                "a,b,c",
                "2,3,x2",
                "3,x,1",
            ],
        )

    def test_filter_easy(self):
        """as expected, a filter pattern that matches everything returns all the rows"""
        self.assertLines(
            ["-F", "(?=.)", "z", "examples/dummy2.csv"],
            [
                "a,b,c",
                "z1,z2,z3",
                "z8,z9,z1z0",
            ],
        )

    def test_filter_easy_null(self):
        """a filter that matches everything but effectively does nothing"""
        self.assertLines(
            ["-F", "(?=.)", "", "examples/dummy2.csv"],
            [
                "a,b,c",
                "1,2,3",
                "8,9,10",
            ],
        )

    def test_filter_harsh(self):
        """
        as expected, a filter pattern that matches nothing should return no rows except header
        """
        self.assertLines(
            ["-F", "x", "y", "examples/dummy2.csv"],
            [
                "a,b,c",
            ],
        )

    def test_filter_literal_match(self):
        tdata = "\n".join(
            [
                "a,b",
                "x,42",
                r"y,\d",
            ]
        )
        with stdin_as_string(StringIO(tdata)):
            self.assertLines(
                [
                    "-F",
                    "-m",
                    r"\d",
                    r"\1",
                ],
                [
                    "a,b",
                    r"y,\1",
                ],
            )


class TestColumnChoice(TestCSVSed):
    @property
    def idata(self):
        rows = ["id,name,val", "1,2,3x", "3,4,5", "6,7y,8z"]
        return StringIO("\n".join(rows))

    def test_columns_by_name(self):
        """only specified columns are affected"""
        with stdin_as_string(self.idata):
            self.assertLines(
                ["-c", "id,val", r"(\w+)", r"\1!"],
                ["id,name,val", "1!,2,3x!", "3!,4,5!", "6!,7y,8z!"],
            )

    def test_columns_by_index(self):
        """only specified columns are affected"""
        with stdin_as_string(self.idata):
            self.assertLines(
                ["-c", "3,1", r"(\w+)", r"\1!"],
                ["id,name,val", "1!,2,3x!", "3!,4,5!", "6!,7y,8z!"],
            )

    def test_columns_by_zero_index(self):
        """only specified columns are affected"""
        with stdin_as_string(self.idata):
            self.assertLines(
                [
                    "-c",
                    "2,0",
                    r"(\w+)",
                    r"\1!",
                    "--zero",
                ],
                ["id,name,val", "1!,2,3x!", "3!,4,5!", "6!,7y,8z!"],
            )

    def test_filtered_columns(self):
        """only selected columns are affected, AND filtered for"""
        with stdin_as_string(self.idata):
            self.assertLines(
                [
                    "-F",
                    "-c",
                    "id,name",
                    r"([3-9])",
                    r"\1@",
                ],
                [
                    "id,name,val",
                    "3@,4@,5",
                    "6@,7@y,8z",
                ],
            )

        # variation...
        with stdin_as_string(self.idata):
            self.assertLines(
                [
                    "-Fc",
                    "2",
                    r"[a-z]",
                    r"$",
                ],
                [
                    "id,name,val",
                    "6,7$,8z",
                ],
            )

    def test_old_basic(self):
        """deprecate"""
        self.assertLines(
            ["-c", "b,c", r"(\w)", r"\1!", "examples/dummy.csv"],
            [
                "a,b,c",
                "1,2!,3!",
            ],
        )


###################################################################################################
### Tests that verify my documentation examples
###################################################################################################
class TestDocExamples(TestCSVSed):
    """Tests that verify my documentation examples"""

    @property
    def idata(self):
        rows = ["id,name,val", "1,2,3x", "3,4,5", "6,7y,8z"]
        return StringIO("\n".join(rows))

    def test_intro(self):
        datacsv = StringIO("id,name\n1,Mrs. Adams\n2,Miss Miller\n3,Mrs Smith\n")
        with stdin_as_string(datacsv):
            self.assertLines(
                [
                    r"(Mrs|Miss|Ms)\.?",
                    "Ms.",
                ],
                [
                    "id,name",
                    "1,Ms. Adams",
                    "2,Ms. Miller",
                    "3,Ms. Smith",
                ],
            )

    def test_hacky_strip(self):
        """obv you should use csvnorm, but this works in a pinch"""
        self.assertLines(
            [r"^\s*(.+?)\s*$", r"\1", "examples/ws_consec.csv"],
            [
                "id,phrase",
                "1,hello world",
                "2,good   bye",
                "3,a  ok",
            ],
        )

    def test_usage_filter_example(self):
        """
        $ csvsed -F '[a-z]' '%' data.csv
        """
        with stdin_as_string(self.idata):
            self.assertLines(
                [
                    "-F",
                    "[a-z]",
                    "%",
                ],
                ["id,name,val", "1,2,3%", "6,7%,8%"],
            )


###################################################################################################
###################################################################################################
###
### Tests of edge cases or experimental functionality or just obsolete
###
###################################################################################################
###################################################################################################


class TestExpressionArguments(TestCSVSed):
    """
    make sure first_patttern + first_replace are properly interpreted;

    this section previously dealt with multiple expression functionality. That functionality has been deprecated/made
    experimental, so this test section can probably be deleted/ignored
    """

    def test_ez(self):
        """input_file always has to come after pattern and replace; this test is probably redundant"""
        self.assertLines(
            [r"(\w)", r"\1!", "examples/dummy.csv"],
            [
                "a,b,c",
                "1!,2!,3!",
            ],
        )

    def test_filter_mode_uses_first_expression_only(self):
        """
        The additional expr should still have a substitution effect, but it
            should NOT limit the rows returned

        Note: currently not used as '-E' is still experimental
        """

        self.assertLines(
            ["-F", "3", "9", "examples/dummy5.csv", "-E", r"\d{2,}", "X"],
            [
                "a,b,c",
                "1,2,9",
                "2,9,X",
                "9,4,1",
            ],
        )


class TestEdgeCases(TestCSVSed):
    """TODO a lot of these tests may be redundant or obsolete"""

    ######################################
    # test intermixed args
    ######################################

    def test_with_columns_opt_upfront(self):
        self.assertLines(
            [
                "-c",
                "value",
                r"my (\w{5,})",
                r"Your \1!",
                "examples/myway.csv",
            ],
            [
                "code,value",
                "1,Your money!",
                '2,"Your stuff!, my way"',
                "3,your house has my car",
            ],
        )

    def test_intermix_columns_option(self):
        # -c option before required args
        self.assertLines(
            [
                "-c",
                "a,c",
                r"(\w)",
                r"\1!",
                "examples/dummy.csv",
            ],
            [
                "a,b,c",
                "1!,2,3!",
            ],
        )

        # -c option after required args
        self.assertLines(
            [r"(\w)", r"\1!", "examples/dummy.csv", "-c", "a,c"],
            [
                "a,b,c",
                "1!,2,3!",
            ],
        )

        # -c option mixed up in there
        self.assertLines(
            [
                r"(\w)",
                "-c",
                "a,c",
                r"\1!",
                "examples/dummy.csv",
            ],
            [
                "a,b,c",
                "1!,2,3!",
            ],
        )

    def test_intermix_just_required_args_and_explicit_stdin(self):
        infile = StringIO("a,b,c\n1,2,3\n")
        with stdin_as_string(infile):
            self.assertLines(
                [
                    r"(\w)",
                    r"\1!",
                    "-",
                ],
                [
                    "a,b,c",
                    "1!,2!,3!",
                ],
            )
            infile.close()

        # -c option in the middle of stuff
        infile = StringIO("a,b,c\n1,2,3\n")
        with stdin_as_string(infile):
            self.assertLines(
                [
                    r"(\w)",
                    r"\1!",
                    "-c",
                    "a,c",
                    "-",
                ],
                [
                    "a,b,c",
                    "1!,2,3!",
                ],
            )
            infile.close()

    def test_intermix_just_required_args_and_implicit_stdin(self):
        infile = StringIO("a,b,c\n1,2,3\n")
        with stdin_as_string(infile):
            self.assertLines(
                [
                    r"(\w)",
                    r"\1!",
                ],
                [
                    "a,b,c",
                    "1!,2!,3!",
                ],
            )
            infile.close()

        # -c option in the middle of stuff
        infile = StringIO("a,b,c\n1,2,3\n")
        with stdin_as_string(infile):
            self.assertLines(
                [
                    r"(\w)",
                    r"\1!",
                    "-c",
                    "a,c",
                ],
                [
                    "a,b,c",
                    "1!,2,3!",
                ],
            )
            infile.close()

    def test_no_error_when_expression_has_2_args_and_piped_input(self):
        self.assertCmdLines(
            r"""cat examples/dummy.csv | csvsed '(1|2)' '\1x'""", ["a,b,c", "1x,2x,3"]
        )

        # note: assertPipedLines will probably be deprecated
        self.assertPipedLines(
            [["cat", "examples/dummy.csv"], ["csvsed", "(1|2)", r"\1x"]],
            ["a,b,c", "1x,2x,3"],
        )

        # old test, deprecated:
        # p1 = Popen(
        #     [
        #         "cat",
        #         "examples/dummy.csv",
        #     ],
        #     stdout=PIPE,
        # )
        # p2 = Popen(["csvsed", "(1|2)", r"\1x"], stdin=p1.stdout, stdout=PIPE)
        # p1.stdout.close()
        # p1.wait()
        # txt = p2.communicate()[0].decode("utf-8")
        # p2.wait()
        # self.assertEqual(txt.splitlines(), ["a,b,c", "1x,2x,3"])

    ##############################
    # special stuff
    ##############################

    def test_pattern_arg_has_leading_hyphen_causes_error(self):
        ioerr = StringIO()
        with contextlib.redirect_stderr(ioerr):
            with self.assertRaises(SystemExit) as e:
                u = self.get_output([r"-\d", r"@\d", "examples/ledger.csv"])

        self.assertEqual(e.exception.code, 2)
        self.assertIn(r"unrecognized arguments: -\d", ioerr.getvalue())
        # todo later
        # self.assertIn(rf"""If you are trying to match a pattern that begins with a hyphen, put a backslash before that hyphen, e.g. '\-\d' """, ioerr.getvalue())

    def test_pattern_arg_has_leading_hyphen_escaped(self):
        self.assertLines(
            [
                "-F",
                r"\-(\d)",
                r"@\1",
                "examples/ledger.csv",
            ],
            [
                "id,name,revenue,gross",
                # '001,apples,21456,$3210.45',
                # '002,bananas,"2,442","-$1,234"',
                # '003,cherries,"$9,700.55","($7.90)"',
                # '004,dates,4 102 765.33,18 765',
                # '005,eggplants,"$3,987",$501',
                # '006,figs,"$30,333","(777.66)"',
                '006,grapes,"154,321.98","@32,654"',
            ],
        )

    def test_pattern_arg_has_leading_hyphen_double_escaped(self):
        self.assertLines(
            [
                "-F",
                r"\\-(\d)",
                r"@\1",
                "examples/ledger.csv",
            ],
            [
                "id,name,revenue,gross",
                # '001,apples,21456,$3210.45',
                # '002,bananas,"2,442","-$1,234"',
                # '003,cherries,"$9,700.55","($7.90)"',
                # '004,dates,4 102 765.33,18 765',
                # '005,eggplants,"$3,987",$501',
                # '006,figs,"$30,333","(777.66)"',
            ],
        )

    def test_repl_arg_has_leading_hyphen_escaped(self):
        self.assertLines(
            [
                "-F",
                r"\-(\d)",
                r"\-X\1",
                "examples/ledger.csv",
            ],
            [
                "id,name,revenue,gross",
                # '001,apples,21456,$3210.45',
                # '002,bananas,"2,442","-$1,234"',
                # '003,cherries,"$9,700.55","($7.90)"',
                # '004,dates,4 102 765.33,18 765',
                # '005,eggplants,"$3,987",$501',
                # '006,figs,"$30,333","(777.66)"',
                '006,grapes,"154,321.98","-X32,654"',
            ],
        )
