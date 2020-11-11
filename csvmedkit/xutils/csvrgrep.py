#!/usr/bin/env python

"""
csvrgrep is experimental/unofficial for now
"""

from argparse import Action
from os import isatty
import sys
from typing import Iterable as IterableType, List as ListType

from csvmedkit.cmk.cmkutil import CmkMixedUtil
from csvmedkit.cmk.helpers import cmk_filter_rows


class CSVRgrep(CmkMixedUtil):
    description = "Like csvgrep, except with support for multiple expressions"
    override_flags = [
        "f",
    ]

    def add_arguments(self, **kwargs):

        self.argparser.add_argument(
            "-n",
            "--names",
            dest="names_only",
            # nargs='?',
            # action=names_only_mode(),
            action="store_true",
            help="Display column names and indices from the input CSV, then exit.",
        )

        self.argparser.add_argument(
            "-c",
            "--columns",
            dest="columns",
            help='A comma separated list of column indices, names or ranges to be searched, e.g. "1,id,3-5".',
        )

        self.argparser.add_argument(
            "-E",
            "--expr",
            dest="expressions_list",
            action="append",
            nargs="*",
            help="Store a list of patterns to match",
        )

        self.argparser.add_argument(
            "-m",
            "--literal-match",
            dest="literal_match",
            action="store_true",
            default=False,
            # nargs='?',
            help="Match patterns literally instead of using regular expressions",
        )

        self.argparser.add_argument(
            "-i",
            "--invert-match",
            dest="inverse",
            action="store_true",
            help="If specified, select non-matching instead of matching rows.",
        )
        self.argparser.add_argument(
            "-a",
            "--all-match",
            dest="all_match",
            action="store_true",
            help="If specified, only select rows for which every column matches the given pattern",
        )

        self.argparser.add_argument(
            metavar="PATTERN",
            dest="first_pattern",
            nargs="?",
            type=str,
            help="A pattern to search for",
        )

        self.argparser.add_argument(
            metavar="FILE",
            nargs="?",
            dest="input_path",
            help="The CSV file to operate on. If omitted, will accept input as piped data via STDIN.",
        )

    def _handle_expressions(self) -> ListType:
        expressions = []
        first_pattern = self.args.first_pattern
        first_colstring = self.args.columns if self.args.columns else ""
        expressions.append([first_pattern, first_colstring])

        exlist = getattr(self.args, "expressions_list")
        if exlist:
            for i, _e in enumerate(exlist):
                ex = _e.copy()
                if len(ex) < 1 or len(ex) > 2:
                    self.argparser.error(
                        f"""-E/--expr takes 1 or 2 arguments, not {len(ex)}: {ex}"""
                    )

                if len(ex) == 1:
                    # blank column_str argument is interpreted as "use -c/--columns value"
                    ex.append(first_colstring)

                expressions.append(ex)

        return expressions

    def main(self):

        if self.additional_input_expected():
            if len(self.last_expr) == 1:
                self.log_err(
                    f"""WARNING: the last positional argument – {self.last_expr[0]} – is interpreted as the first and only argument to -E/--expr, i.e. the pattern to search for."""
                )
                self.log_err(
                    "Make sure that it isn't meant to be the name of your input file!\n"
                )
            self.log_err(
                "No input file or piped data provided. Waiting for standard input:"
            )

        self.expressions = self._handle_expressions()

        _all_match = self.args.all_match
        _any_match = not _all_match
        _inverse = self.args.inverse
        _literal_match = self.args.literal_match
        _column_offset = self.get_column_offset()

        if self.writer_kwargs.pop("line_numbers", False):
            self.reader_kwargs["line_numbers"] = True

        xrows, column_names, column_ids = self.get_rows_and_column_names_and_column_ids(
            **self.reader_kwargs
        )

        for epattern, ecolstring in self.expressions:
            xrows = cmk_filter_rows(
                xrows,
                epattern,
                ecolstring,
                column_names,
                column_ids,
                literal_match=_literal_match,
                column_offset=_column_offset,
                inverse=_inverse,
                any_match=_any_match,
                # not_columns=_not_columns,
            )

        outs = self.text_csv_writer()
        outs.writerow(column_names)
        outs.writerows(xrows)

    def run(self):
        """
        A wrapper around the main loop of the utility which handles opening and
        closing files.
        """
        if self.args.names_only:
            if not self.args.first_pattern and self.args.input_path:
                ifile = self.args.input_path
            elif self.args.first_pattern and not self.args.input_path:
                ifile = self.args.first_pattern
            else:
                ifile = None

            self.input_file = self._open_input_file(ifile)
            self.print_column_names()
            self.input_file.close()
            return

        # at this point, we need to throw an error if at least one positional argument wasn't found
        if not self.args.first_pattern:
            self.argparser.error(
                "Must provide a [PATTERN] argument, e.g. `csvrgrep '[a-z]+' data.csv`"
            )

        self.last_expr = []
        if not self.args.input_path:
            # then it must have been eaten by an -E flag; we assume the input file is in last_expr[-1],
            # where `last_expr` is the last member of expressions_list
            if self.args.expressions_list:
                self.last_expr = self.args.expressions_list[-1]

                if len(self.last_expr) > 1:
                    # could be either 2 or 3
                    self.args.input_path = self.last_expr.pop()
                elif len(self.last_expr) == 1:
                    pass
                    # do nothing, but be warned that if there is no stdin,
                    # then -E might have eaten up the input_file argument
                    # and interpreted it as pattern
                else:
                    # else, last_expr has an implied second argument, and
                    # input_path is hopefully stdin
                    self.args.input_path = None

        self.input_file = self._open_input_file(self.args.input_path)
        super().run()


def launch_new_instance():
    utility = CSVRgrep()
    utility.run()


if __name__ == "__main__":
    launch_new_instance()
