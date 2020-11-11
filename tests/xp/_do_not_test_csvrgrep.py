"""
csvrgrep is in experimental status
"""

import contextlib
from io import StringIO

import sys

from tests.mk import (
    CmkTestCase,
    ColumnsTests,
    EmptyFileTests,
    NamesTests,
    patch,
    skiptest,
)
from csvmedkit.xutils.csvrgrep import CSVRgrep, launch_new_instance
from csvmedkit.exceptions import *

# i.e. as opposed to `csvrgrep`; CLI_PATH is used since csvrgrep is not an entry point
CLI_PATH = "./csvmedkit/xutils/csvrgrep.py"


class TestCSVRgrep(CmkTestCase, EmptyFileTests, ColumnsTests, NamesTests):

    Utility = CSVRgrep
    default_args = [
        r"\d",
        "examples/dummy.csv",
    ]
    columns_args = [
        r"\d+",
    ]

    def test_launch_new_instance(self):
        with patch.object(
            sys,
            "argv",
            [self.Utility.__name__.lower()] + self.default_args
            # + ["examples/dummy.csv"],
        ):
            launch_new_instance()

    def test_skip_lines(self):
        self.assertRows(
            [
                "--skip-lines",
                "3",
                "-c",
                "a,b",
                "1",
                "examples/test_skip_lines.csv",
            ],
            [
                ["a", "b", "c"],
                ["1", "2", "3"],
            ],
        )

    def test_basic(self):
        """
        a,b,c
        1,2,3
        2,3,42
        3,4,1
        22,99,222
        """
        self.assertRows(
            [r"\d{2}", "examples/dummy5.csv"],
            [["a", "b", "c"], ["2", "3", "42"], ["22", "99", "222"]],
        )

    def test_basic_column_arg(self):
        """
        a,b,c
        1,2,3
        2,3,42
        3,4,1
        22,99,222
        """
        self.assertRows(
            [
                r"3|22",
                "examples/dummy5.csv",
                "-c",
                "b,c",
            ],
            [["a", "b", "c"], ["1", "2", "3"], ["2", "3", "42"], ["22", "99", "222"]],
        )

    def test_two_patterns(self):
        """
        a,b,c
        1,2,3
        2,3,42
        3,4,1
        22,99,222
        """
        self.assertRows(
            [
                "-c",
                "b,c",
                "3|22",
                "-E",
                r"^\d$",
                "examples/dummy5.csv",
            ],
            [["a", "b", "c"], ["1", "2", "3"], ["2", "3", "42"]],
        )

    def test_multi_patterns_explicit_col_arg(self):
        """

        1,2,3
        2,3,42
        3,4,1
        22,99,222
        """
        self.assertLines(
            [
                "-c",
                "b,c",
                "3|22",
                "-E",
                r"^\d$",
                "c",
                "examples/dummy5.csv",
            ],
            ["a,b,c", "1,2,3"],
        )

    ######################################################################
    # test match modes
    ######################################################################

    def test_basic_literal_match(self):
        self.assertRows(
            ["-m", r"\d{2}", "examples/dummy5.csv"],
            [
                ["a", "b", "c"],
            ],
        )

        self.assertRows(
            ["-m", "-c", "c", "22", "examples/dummy5.csv"],
            [["a", "b", "c"], ["22", "99", "222"]],
        )

    def test_all_match(self):
        """TODO: can't mix and match positional and optional args?"""
        self.assertLines(
            ["-a", "-c", "a,c", r"\d{2,}", "examples/dummy5.csv"],
            [
                "a,b,c",
                "22,99,222",
            ],
        )

    ######################################################################
    # multi expressions
    ######################################################################

    def test_multi_expression_basic(self):
        self.assertLines(
            ["2", "-E", r"1|3", "examples/dummy5.csv"],
            [
                "a,b,c",
                "1,2,3",
                "2,3,42",
            ],
        )

    def test_multi_expression_variable_expr_args(self):
        self.assertLines(
            ["2", "-m", "-E", r"3", "b,c", "-E", "2", "examples/dummy5.csv"],
            [
                "a,b,c",
                "1,2,3",
                "2,3,42",
            ],
        )

    def test_expr_col_arg_overrides_main_columns_flag(self):
        """
        if the expression has a column str other than '', then its list of column_ids to grep
        takes precedence over  -c/--columns
        """
        self.assertLines(
            ["-c", "a,c", "2", "-E", r"\d{2,}", "b", "examples/dummy5.csv"],
            [
                "a,b,c",
                "22,99,222",
            ],
        )

    def test_expr_col_arg_defaults_to_main_columns_flag(self):
        """
        if the expression has a blank column str, then it uses whatever -c/--columns is set to

        (and if -c is unset, then all columns are grepped)

        1,2,3
        2,3,42
        3,4,1
        22,99,222
        """
        self.assertLines(
            [
                "-c",
                "c,a",
                "2",
                "-E",
                r"\d{2,}",
                "a,b,c",
                "-E",
                "4",
                "examples/dummy5.csv",
            ],
            [
                "a,b,c",
                "2,3,42",
            ],
        )

        self.assertLines(
            ["-c", "a,b", "2", "-E", "3", "examples/dummy5.csv"],
            [
                "a,b,c",
                "2,3,42",
            ],
        )

    def test_multi_expressions_are_ANDed_not_ORed(self):
        self.assertLines(
            [
                ".+",
                "examples/hamlet.csv",
                "--expr",
                r"^[HL]",
                "speaker",
                "--expr",
                r"[^1]",
                "act",
                "--expr",
                r"\w{6,}",
            ],
            [
                "act,scene,speaker,lines",
                "4,7,Laertes,Know you the hand?",
            ],
        )

    ######################################
    # discerning input_file/stdin argument
    ######################################

    def test_when_single_pattern_and_no_input_file(self):
        r"""
        cat data.txt | csvrgrep '4'
        """
        # p1 = Popen(["cat", "examples/dummy5.csv"], stdout=PIPE)
        # p2 = Popen(
        #     [
        #         CLI_PATH,
        #         "4",
        #     ],
        #     stdin=p1.stdout,
        #     stdout=PIPE,
        # )
        # p1.stdout.close()
        # p1.wait()
        # txt = p2.communicate()[0].decode("utf-8")
        # p2.wait()

        # lines = txt.splitlines()
        self.assertCmdLines(
            "cat examples/dummy5.csv | csvrgrep '4'",
            [
                "a,b,c",
                "2,3,42",
                "3,4,1",
            ],
        )

    def test_when_last_expr_has_just_one_arg_and_no_input_file(self):
        r"""
        cat data.txt | csvrgrep '1' -E '4'
        """
        # p1 = Popen(["cat", "examples/dummy5.csv"], stdout=PIPE)
        # p2 = Popen([CLI_PATH, "1", "-E", "4"], stdin=p1.stdout, stdout=PIPE)
        # p1.stdout.close()
        # p1.wait()
        # txt = p2.communicate()[0].decode("utf-8")
        # p2.wait()

        # lines = txt.splitlines()
        self.assertCmdLines(
            """cat examples/dummy5.csv | csvrgrep '1' -E '4'""",
            [
                "a,b,c",
                "3,4,1",
            ],
        )

    ######################################
    # special names test
    ######################################

    @skiptest("csvrgrep is not a registered entry point")
    def test_names_mode_with_stdin(self):
        # p1 = Popen(["cat", "examples/dummy.csv"], stdout=PIPE)
        # p2 = Popen([CLI_PATH, "-n"], stdin=p1.stdout, stdout=PIPE)
        # p1.stdout.close()
        # p1.wait()
        # txt = p2.communicate()[0].decode("utf-8")
        # p2.wait()

        # lines = [t.strip() for t in txt.splitlines()]
        self.assertCmdLines(
            """cat examples/dummy.csv | csvrgrep -n""",
            [
                "1: a",
                "2: b",
                "3: c",
            ],
        )

    ######################################
    # errors
    ######################################

    def test_error_when_no_pattern_and_no_input_file(self):
        ioerr = StringIO()
        with contextlib.redirect_stderr(ioerr):
            with self.assertRaises(SystemExit) as e:
                u = self.get_output([])

        self.assertEqual(e.exception.code, 2)
        self.assertIn("Must provide a [PATTERN] argument", ioerr.getvalue())

    def test_error_when_no_pattern_but_additional_expressions(self):
        """"todo, maybe redundant"""
        ioerr = StringIO()
        with contextlib.redirect_stderr(ioerr):
            with self.assertRaises(SystemExit) as e:
                u = self.get_output(["-E", "1", "examples/dummy.csv"])

        self.assertEqual(e.exception.code, 2)
        self.assertIn("Must provide a [PATTERN] argument", ioerr.getvalue())

    def test_error_when_expression_has_0_args(self):
        ioerr = StringIO()
        with contextlib.redirect_stderr(ioerr):
            with self.assertRaises(SystemExit) as e:
                u = self.get_output(["-E", "-m", "PATTERN", "examples/dummy.csv"])

        self.assertEqual(e.exception.code, 2)
        self.assertIn("-E/--expr takes 1 or 2 arguments, not 0:", ioerr.getvalue())

    def test_error_when_expression_has_more_than_2_args(self):
        ioerr = StringIO()
        with contextlib.redirect_stderr(ioerr):
            with self.assertRaises(SystemExit) as e:
                u = self.get_output(
                    [
                        "PATTERN",
                        "examples/dummy.csv",
                        "-E",
                        "a",
                        "b",
                        "c",
                    ]
                )

        self.assertEqual(e.exception.code, 2)
        self.assertIn("-E/--expr takes 1 or 2 arguments, not 3:", ioerr.getvalue())

    def test_no_error_when_expression_has_1_args_and_piped_input(self):
        p1 = Popen(
            [
                "cat",
                "examples/dummy.csv",
            ],
            stdout=PIPE,
        )
        p2 = Popen(
            [
                CLI_PATH,
                "2|1",
                "-E",
                "1|2",
            ],
            stdin=p1.stdout,
            stdout=PIPE,
        )
        p1.stdout.close()
        p1.wait()
        txt = p2.communicate()[0].decode("utf-8")
        p2.wait()
        self.assertEqual(txt.splitlines(), ["a,b,c", "1,2,3"])

    @skiptest("because I dont know how to deal with stdin.isatty holdup")
    def test_error_when_final_expression_eats_up_input_path(self):
        ioerr = StringIO()
        old_stdin = sys.stdin

        with contextlib.redirect_stderr(ioerr):
            # with self.assertRaises(SystemExit) as e:
            args = ["-E", "1", "-E", "2", "-E", "examples/dummy.csv"]
            # p = Process(target=self.get_output, args=(args,))
            # p.start()
            sys.stdin = StringIO("a,b,c\n1,2,3\n")
            # p.join()

            self.assertIn("WARNING", ioerr.getvalue())

        # self.assertEqual(e.exception.code, 2)
        # clean up stdin
        sys.stdin = oldstdin
        exit
