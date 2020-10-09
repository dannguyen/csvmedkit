"""
These are tests on csvsed's experimental features, i.e. multiple expressions, which are
currently hidden from the API
"""

import contextlib
from io import StringIO
from subprocess import Popen, PIPE
import sys
from unittest import skip as skiptest
from tests.tk import CSVKitTestCase, stdin_as_string
from csvmedkit.moreutils.csvsed import CSVSed


class TestCSVSed(CSVKitTestCase):
    Utility = CSVSed

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

    ################################################################
    # intermix + multiple expressions, something we might cut out(?)
    ################################################################

    def test_intermix_multiple_expressions(self):
        # options/extra expressions after required args  [first_pattern] [first_repl] and [input_file]
        self.assertLines(
            [
                r"(\w)",
                r"\1!",
                "examples/dummy.csv",
                "-c",
                "a,c",
                "-E",
                "!",
                "X",
                "c",
                "-E",
                ".",
                "Q",
                "b",
            ],
            [
                "a,b,c",
                "1!,Q,3X",
            ],
        )

        # extra expressions w/ only 2 args each, after required args [first_pattern] [first_repl] and [input_file]
        self.assertLines(
            [
                r"(\w)",
                r"\1!",
                "examples/dummy.csv",
                "-c",
                "a,c",
                "-E",
                "!",
                "X",
                "-E",
                r"[A-Z]",
                "Q",
            ],
            [
                "a,b,c",
                "1Q,2,3Q",
            ],
        )

        # extra expressions between [first_pattern] [first_repl] and [input_file]
        self.assertLines(
            [
                "-c",
                "a,c",
                r"(\w)",
                r"\1!",
                "-E",
                "!",
                "X",
                "c",
                "-E",
                ".",
                "Q",
                "b",
                "examples/dummy.csv",
            ],
            [
                "a,b,c",
                "1!,Q,3X",
            ],
        )

        # extra expressions with only 2 args each, between [first_pattern] [first_repl] and [input_file]
        self.assertLines(
            [
                "-c",
                "a,c",
                r"(\w)",
                r"\1!",
                "-E",
                "!",
                "X",
                "-E",
                ".",
                "Q",
                "examples/dummy.csv",
            ],
            [
                "a,b,c",
                "QQ,2,QQ",
            ],
        )

        # recommended format: column option, required args, extra expressions
        self.assertLines(
            [
                "-c",
                "a,c",
                r"(\w)",
                r"\1!",
                "examples/dummy.csv",
                "-E",
                "!",
                "X",
                "-E",
                r"\w",
                "Z",
                "a,b",
            ],
            [
                "a,b,c",
                "ZZ,Z,3X",
            ],
        )

        # alt recommended format: column option, [first_pattern], [first_replacement], extra expressions, infile
        self.assertLines(
            [
                "-c",
                "a,c",
                r"(\w)",
                r"\1!",
                "-E",
                "!",
                "X",
                "-E",
                r"\w",
                "Z",
                "a,b",
                "examples/dummy.csv",
            ],
            [
                "a,b,c",
                "ZZ,Z,3X",
            ],
        )

    def test_intermix_and_explicit_stdin(self):
        # alt recommended format: stdin piped into: column option, [first_pattern], [first_replacement], extra expressions
        #  and explicit stdin '-'
        infile = StringIO("a,b,c\n1,2,3\n")
        with stdin_as_string(infile):
            self.assertLines(
                [
                    "-c",
                    "a,c",
                    r"(\w)",
                    r"\1!",
                    "-E",
                    "!",
                    "X",
                    "-E",
                    r"\w",
                    "Z",
                    "a,b",
                    "-",
                ],
                [
                    "a,b,c",
                    "ZZ,Z,3X",
                ],
            )
            infile.close()

    def test_intermix_and_implicit_stdin(self):
        # alt recommended format: stdin piped into: column option, [first_pattern], [first_replacement], extra expressions
        #  and explicit stdin '-'
        infile = StringIO("a,b,c\n1,2,3\n")
        with stdin_as_string(infile):
            self.assertLines(
                [
                    "-c",
                    "a,c",
                    r"(\w)",
                    r"\1!",
                    "-E",
                    "!",
                    "X",
                    "-E",
                    r"\w",
                    "Z",
                    "a,b",
                ],
                [
                    "a,b,c",
                    "ZZ,Z,3X",
                ],
            )
            infile.close()

        ## messy edge case of parameter arrangement
        infile = StringIO("a,b,c\n1,2,3\n")
        with stdin_as_string(infile):
            self.assertLines(
                [
                    "-E",
                    "!",
                    "X",
                    "-E",
                    r"\w",
                    "Z",
                    "a,b",
                    "-c",
                    "a,c",
                    r"(\w)",
                    r"\1!",
                ],
                [
                    "a,b,c",
                    "ZZ,Z,3X",
                ],
            )
            infile.close()

    ##############################
    # error stuff
    ##############################

    def test_error_when_expression_has_0_args(self):
        ioerr = StringIO()
        with contextlib.redirect_stderr(ioerr):
            with self.assertRaises(SystemExit) as e:
                u = self.get_output(
                    ["-E", "-m", "pattern", "repl", "examples/dummy.csv"]
                )

        self.assertEqual(e.exception.code, 2)
        self.assertIn(
            f"-E/--expr takes 2 or 3 arguments; you provided 0:", ioerr.getvalue()
        )

    def test_error_when_expression_has_1_arg(self):
        ioerr = StringIO()
        with contextlib.redirect_stderr(ioerr):
            with self.assertRaises(SystemExit) as e:
                u = self.get_output(
                    ["-E", "a", "-m", "pattern", "repl", "examples/dummy.csv"]
                )

        self.assertEqual(e.exception.code, 2)
        self.assertIn(
            "-E/--expr takes 2 or 3 arguments; you provided 1: ['a']", ioerr.getvalue()
        )

    def test_error_when_expression_has_more_than_3_args(self):
        ioerr = StringIO()
        with contextlib.redirect_stderr(ioerr):
            with self.assertRaises(SystemExit) as e:
                u = self.get_output(
                    [
                        "pattern",
                        "repl",
                        "examples/dummy.csv",
                        "-E",
                        "a",
                        "b",
                        "c",
                        "d",
                    ]
                )

        self.assertEqual(e.exception.code, 2)
        self.assertIn(
            "-E/--expr takes 2 or 3 arguments; you provided 4: ['a', 'b', 'c', 'd']",
            ioerr.getvalue(),
        )

    @skiptest("because I dont know how to deal with stdin.isatty holdup")
    def test_error_when_final_expression_eats_up_input_path(self):
        ioerr = StringIO()
        old_stdin = sys.stdin

        with contextlib.redirect_stderr(ioerr):
            # with self.assertRaises(SystemExit) as e:
            args = ["-E", "1", "2", "examples/dummy.csv"]
            # p = Process(target=self.get_output, args=(args,))
            # p.start()
            sys.stdin = StringIO("a,b,c\n1,2,3\n")
            # p.join()

            self.assertIn("WARNING", ioerr.getvalue())

        # self.assertEqual(e.exception.code, 2)
        # clean up stdin
        sys.stdin = oldstdin
        exit

    ################################################
    # examples

    def test_example_intro(self):
        r"""
        $ csvsed "Ab[bi].+" "Abby" -E "(B|R)ob.*" "\1ob" -E "(?:Jack|John).*" "John"  examples/aliases.csv
        """
        self.assertLines(
            [
                r"Ab[bi].+",
                "Abby",
                "-E",
                r"(B|R)ob.*",
                r"\1ob",
                "-E",
                r"(?:Jack|John).*",
                r"John",
                "examples/aliases.csv",
            ],
            [
                "id,to,from",
                "1,Abby,Bob",
                "2,Bob,John",
                "3,Abby,John",
                "4,John,Abner",
                "5,Rob,John",
                "6,Jon,Abby",
                "7,Rob,Abby",
            ],
        )
