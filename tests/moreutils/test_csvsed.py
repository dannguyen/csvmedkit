import contextlib
from io import StringIO
from subprocess import Popen, PIPE
import sys

from unittest import skip as skiptest
from unittest.mock import patch
from tests.tk import CSVKitTestCase, ColumnsTests, EmptyFileTests, stdin_as_string

from csvmedkit.exceptions import ColumnIdentifierError
from csvmedkit.moreutils.csvsed import CSVSed, launch_new_instance


class TestCSVSed(CSVKitTestCase, ColumnsTests, EmptyFileTests):
    Utility = CSVSed
    default_args = ["hello", "world"]
    columns_args = [
        "x",
        "y",
    ]

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

    def test_outputs_non_pattern_matches_are_returned(self):
        self.assertLines(
            [r"([a-z])", r"\1!", "examples/tinyvals.csv"],
            [
                "alpha,omega",
                "1,9",
                "a!,z!",
                "$,%",
            ],
        )

    def test_column_choice(self):
        self.assertLines(
            ["-c", "b,c", r"(\w)", r"\1!", "examples/dummy.csv"],
            [
                "a,b,c",
                "1,2!,3!",
            ],
        )

    def test_supports_case_insensitivity(self):
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

    ##############################
    # like grep
    ##############################

    def test_like_grep_mode(self):
        """
        like-grep mode filters, then the sed is applied
        """
        self.assertLines(
            ["-G", "4", "x", "examples/dummy5.csv"],
            [
                "a,b,c",
                "2,3,x2",
                "3,x,1",
            ],
        )

    def test_like_grep_mode_uses_first_expression_only(self):
        """
        The additional expr should still have a substitution effect, but it
            should NOT limit the rows returned
        """

        self.assertLines(
            ["-G", "3", "9", "examples/dummy5.csv", "-E", r"\d{2,}", "X"],
            [
                "a,b,c",
                "1,2,9",
                "2,9,X",
                "9,4,1",
            ],
        )

    ######################################
    # handling multiple expressions via -E
    ######################################

    def test_first_expression(self):
        self.assertLines(
            [r"my (\w{5,})", r"Your \1!", "examples/myway.csv", "-c", "value"],
            [
                "code,value",
                "1,Your money!",
                '2,"Your stuff!, my way"',
                "3,your house has my car",
            ],
        )

    def test_additional_expression(self):
        """
        note how additional expression will use -c setting, when
        its own columns string is missing
        """
        self.assertLines(
            [
                "-c",
                "value",
                r"my (\w{5,})",
                r"Your \1!",
                "examples/myway.csv",
                "-E",
                r"(\w{3,}|\d+)",
                r"_\1_",
            ],
            [
                "code,value",
                "1,_Your_ _money_!",
                '2,"_Your_ _stuff_!, my _way_"',
                "3,_your_ _house_ _has_ my _car_",
            ],
        )

    def test_additional_expression_column_specified(self):
        self.assertLines(
            [
                "-c",
                "value",
                r"my (\w{5,})",
                r"Your \1!",
                "examples/myway.csv",
                "-E",
                r"(\w{3,}|\d+)",
                r"_\1_",
                "value,code",
            ],
            [
                "code,value",
                "_1_,_Your_ _money_!",
                '_2_,"_Your_ _stuff_!, my _way_"',
                "_3_,_your_ _house_ _has_ my _car_",
            ],
        )

    ########## order of operations

    # [
    # 'id,col_a,col_b',
    # '1,hello,world',
    # '2,Hey,you',
    # '3,1,2',
    # '4,9999999,777',
    # '5,OK,Boomer',
    # '6,memory,"Person,woman,man,camera,TV"',]

    def test_order_expressions(self):
        self.assertLines(
            [
                "-c",
                "col_a,col_b",
                r"^(.{1,2})$",  # first pattern
                r"\1\1",  # second pattern
                "-E",
                r"^(.{4})$",
                r"_\1_",
                "id,col_a,col_b",
                "-E",
                r"^(.{6})",
                r"\1, oxford and etc.",
                "col_a",
                "examples/ab.csv",
            ],
            [
                "id,col_a,col_b",
                "1,hello,world",
                "2,Hey,you",
                "3,11,22",
                '4,"999999, oxford and etc.9",777',
                '5,"_OKOK_, oxford and etc.",Boomer',
                '6,"memory, oxford and etc.","Person,woman,man,camera,TV"',
            ],
        )

    def test_order_expressions_literal(self):
        self.assertLines(
            [
                "--match-literal",
                "e",
                "x",
                "examples/ab.csv",
                "-c",
                "col_a,col_b",
                "-E",
                "o",
                "e",
                "col_a,col_b",
                "-E",
                "er",
                "oz",
                "col_a,col_b",
            ],
            [
                "id,col_a,col_b",
                "1,hxlle,wozld",
                "2,Hxy,yeu",
                "3,1,2",
                "4,9999999,777",
                "5,OK,Beemxr",
                '6,mxmozy,"Pxrsen,weman,man,camxra,TV"',
            ],
        )

    def test_order_expressions_plus_grep_mode(self):
        """
        grep_testing happens BEFORE the transformation, thus lines that are
        transformed by the first expression and into something that matches the second
        expression pattern will NOT be returned
        """

        self.assertLines(
            [
                r"^(\d{2,4})$",
                r"\1\1",
                "examples/ab.csv",
                "-G",
                "-E",
                r"(\d{2})",
                r"_\1_",
                "col_a,col_b",
            ],
            [
                "id,col_a,col_b",
                # '1,hello,world',
                # '2,Hey,you',
                # '3,1,2',
                "4,_99__99__99_9,_77__77__77_",
                # '5,OK,Boomer',
                # '6,memory,"Person,woman,man,camera,TV"',
            ],
        )

    ######################################
    # test intermixed args
    ######################################

    def test_intermix_just_required_args(self):
        """input_file always has to come after pattern and replace"""
        self.assertLines(
            [r"(\w)", r"\1!", "examples/dummy.csv"],
            [
                "a,b,c",
                "1!,2!,3!",
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
        p1 = Popen(
            [
                "cat",
                "examples/dummy.csv",
            ],
            stdout=PIPE,
        )
        p2 = Popen(["csvsed", "(1|2)", r"\1x"], stdin=p1.stdout, stdout=PIPE)
        p1.stdout.close()
        p1.wait()
        txt = p2.communicate()[0].decode("utf-8")
        p2.wait()
        self.assertEqual(txt.splitlines(), ["a,b,c", "1x,2x,3"])

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
                "-G",
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
                "-G",
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
                "-G",
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
