#!/usr/bin/env python
import argparse
from pathlib import Path
from typing import List as ListType

from csvmedkit import re_std as re
from csvmedkit.cmk.cmkutil import CmkMixedUtil
from csvmedkit.cmk.helpers import cmk_filter_rows, cmk_parse_column_ids
from csvmedkit.exceptions import *


class Parser:
    description = """Replaces all instances of [PATTERN] with [REPL]"""

    override_flags = [
        "f",
    ]

    def add_arguments(self):
        self.argparser.add_argument(
            "-c",
            "--columns",
            dest="columns",
            help="""A comma separated list of column indices, names or ranges to be affected, e.g. '1,id,3-5'. Defaults to all columns.""",
        )

        self.argparser.add_argument(
            "-m",
            "--match-literal",
            dest="literal_match",
            action="store_true",
            default=False,
            help="By default, [PATTERN] is assumed to be a regular expression. Set this flag to do a literal match and replacement.",
        )

        self.argparser.add_argument(
            "-F",
            "--filter",
            dest="like_grep",
            action="store_true",
            default=False,
            help="""Only return rows that matched [PATTERN]. This has the same effect as operating on data pre-filtered by ``csvgrep -r (or -m) [PATTERN]`""",
        )

        self.argparser.add_argument(
            metavar="PATTERN",
            dest="first_pattern",
            type=str,
            # nargs='?',
            help="A pattern to search for",
        )

        self.argparser.add_argument(
            metavar="REPL",
            dest="first_repl",
            type=str,
            # nargs='?',
            help="A replacement pattern",
        )

        self.argparser.add_argument(
            metavar="FILE",
            nargs="?",
            dest="input_path",
            help="The CSV file to operate on. If omitted, will accept input as piped data via STDIN.",
        )

        self.argparser.add_argument(
            "-E",
            "--expr",
            dest="expressions_list",
            nargs="*",
            action="append",
            type=str,
            help=argparse.SUPPRESS
            # r"""
            # When you want to do multiple sed_expressions:
            #     -E 'PATTERN' 'REPL' '[names_of_columns]'
            #     'names_of_columns' is a comma-delimited list of columns. Omit or leave blank to match the columns specified by '-c/--columns'
            # e.g.
            # -E '(?i)\b(bob|bobby|rob)\b' 'Robert' 'first_name' \
            # -E '^(?i)smith$' 'SMITH' 'last_name' \
            # -E '(\d{2})-(\d{3})' '$1:$2' \
            # """,
        )


class Props:
    @property
    def literal_match_mode(self) -> bool:
        return self.args.literal_match

    @property
    def like_grep(self) -> bool:
        return self.args.like_grep


class CSVSed(Props, Parser, CmkMixedUtil):
    def _handle_sed_expressions(self, column_names: ListType[str]) -> ListType:
        """
        Standard usage of csvsed expects only a single sed expression, so in practice, this
            method returns a list of 1

        Experimental: `-E` can be used to add extra expressions
        """

        # TODO: fix this spaghetti CRAP: maybe make expressions handle dicts/named typles instead of lists
        first_col_str = self.columns_filter or ""
        first_expr = [self.args.first_pattern, self.args.first_repl, first_col_str]
        expressions = [first_expr]
        if list_expressions := getattr(self.args, "expressions_list", []):
            for i, _e in enumerate(list_expressions):
                ex = _e.copy()

                if len(ex) < 2 or len(ex) > 3:
                    self.argparser.error(
                        f"-E/--expr takes 2 or 3 arguments; you provided {len(ex)}: {ex}"
                    )

                if len(ex) == 2:
                    ex.append(first_col_str)

                expressions.append(ex)

        for ex in expressions:
            # this branch re-loops through the_expressions and fixes any leading dashes in the repls
            if ex[1][0:2] == r"\-":
                ex[1] = ex[1][1:]

            # compile the pattern into a regex
            if not self.literal_match_mode:
                ex[0] = re.compile(ex[0])

            # set the column_ids
            ex[2] = cmk_parse_column_ids(ex[2], column_names, self.column_offset)

        return expressions

    def _experimental_multiple_expression_handling(self):
        """
        support of multiple expressions is an experimental feature and may be cut (look at this spaghetti!)
        """

        # this should be a property
        self.last_expr: list = []

        if not self.args.input_path:
            # then it must have been eaten by an -E flag; we assume the input file is in last_expr[-1],
            # where `last_expr` is the last member of expressions_list

            # TODO: maybe refactor this
            if self.args.expressions_list:
                self.last_expr = self.args.expressions_list[-1]

                if len(self.last_expr) > 2:
                    # could be either 3 or 4
                    # test if last part of the expr is actually a file
                    # TODO: this is a bit of a hack; note that it will fail in the edge case where user provides
                    #   a columns argument that somehow manages to be the name of an existing file(???)
                    _xarg = self.last_expr[-1]
                    if Path(_xarg).is_file():
                        self.args.input_path = self.last_expr.pop()
                    elif _xarg == "-":
                        # TODO: should we deprecate explicit '-'?
                        # there's no feasible scenario for a column to be named '-', so we assume its the explicit stdin operator
                        self.last_expr.pop()  # throw minus away
                        self.args.input_path = None  # expect stdin to provide the data
                    else:
                        self.args.input_path = None  # expect stdin to provide the data
                elif len(self.last_expr) == 2:
                    # do nothing, but be warned that if there is no stdin,
                    # then -E might have eaten up the input_file argument
                    # and interpreted it as pattern
                    self.args.input_path = None
                else:
                    # else, last_expr has an implied third argument, and
                    # input_path is hopefully stdin
                    self.args.input_path = None

            # this was originally handled in main; need to rethink and refactor
            # if self.additional_input_expected():
            #     if len(self.last_expr) == 2:
            #         stderr.write(
            #             f"""WARNING: the last positional argument – {self.last_expr[0]} – is interpreted as the first and only argument to -E/--expr, i.e. the pattern to search for.\n"""
            #         )
            #         stderr.write(
            #             "Make sure that it isn't meant to be the name of your input file!\n\n"
            #         )
            #     stderr.write(
            #         "No input file or piped data provided. Waiting for standard input:\n"
            #     )

    def run(self):
        self._experimental_multiple_expression_handling()
        self.input_file = self._open_input_file(self.args.input_path)
        super().run()

    def main(self):
        if self.additional_input_expected():
            stderr.write(
                "No input file or piped data provided. Waiting for standard input:\n"
            )

        if self.writer_kwargs.pop("line_numbers", False):
            self.reader_kwargs["line_numbers"] = True

        xrows, column_names, column_ids = self.get_rows_and_column_names_and_column_ids(
            **self.reader_kwargs
        )

        self.expressions = self._handle_sed_expressions(column_names)

        # here's where we emulate csvrgrep...
        if self.like_grep:
            epattern = self.args.first_pattern
            xrows = cmk_filter_rows(
                xrows,
                epattern,
                self.columns_filter,
                column_names,
                column_ids,
                literal_match=self.literal_match_mode,
                column_offset=self.column_offset,
                inverse=False,
                any_match=True,
            )

        outs = self.text_csv_writer()
        outs.writerow(column_names)
        for row in xrows:
            new_row = []

            for cid, val in enumerate(row):
                newval = val

                for ex in self.expressions:
                    pattern, repl, col_ids = ex
                    if cid in col_ids:
                        repl = fr"{repl}"

                        newval = (
                            pattern.sub(repl, newval)
                            if not self.literal_match_mode
                            else newval.replace(pattern, repl)
                        )
                new_row.append(newval)
                # end of expression-iteration; move on to the next column val

            outs.writerow(new_row)


def launch_new_instance():
    utility = CSVSed()
    utility.run()


if __name__ == "__main__":
    launch_new_instance()
