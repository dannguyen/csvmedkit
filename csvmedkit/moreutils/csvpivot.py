import csv
from collections import namedtuple
import sys
from typing import (
    List as typeList,
    NoReturn as typeNoReturn,
    Tuple as typeTuple,
    Optional as typeOptional,
)

from csvmedkit import agate
from csvmedkit.aggs import Aggy, Aggregates
from csvmedkit.exceptions import *
from csvmedkit.cmk.cmkutil import CmkUtil
from csvmedkit.cmk.helpers import cmk_parse_column_ids, cmk_parse_delimited_str


class Parser:
    """
    Functionality related to command-line configuration and argument handling
    """

    description = """Do a simple pivot table, by row, column, or row and column"""
    override_flags = ["l"]

    def add_arguments(self):
        self.argparser.add_argument(
            "-y",
            "--snifflimit",
            dest="sniff_limit",
            type=int,
            help='Limit CSV dialect sniffing to the specified number of bytes. Specify "0" to disable sniffing entirely.',
        )
        self.argparser.add_argument(
            "-I",
            "--no-inference",
            dest="no_inference",
            action="store_true",
            help="Disable type inference when parsing the input.",
        )

        self.argparser.add_argument(
            "-r",
            "--pivot-rows",
            dest="pivot_rows",
            type=str,
            help="""The column name(s) on which to use as pivot rows. Should be either one name
                                    (or index) or a comma-separated list with one name (or index)""",
        )

        self.argparser.add_argument(
            "-c",
            "--pivot-column",
            dest="pivot_column",
            type=str,
            help="Optionally, a column name/id to use as a pivot column. Only one is allowed",
        )

        self.argparser.add_argument(
            "-a",
            "--agg",
            dest="pivot_aggregate",
            type=str,
            default="count",
            help="""The name of an aggregation to perform on each group of data in the pivot table.
                                    For aggregations that require an argument (i.e. a column name), pass in the aggregation name,
                                    followed by a colon, followed by comma-delimited arguments,
                                     e.g. `-a "sum:age"` and `-a "count:name,hello"

                                    To see a list, run `csvpivot -L/--list-aggs`
                                    """,
        )

        self.argparser.add_argument(
            "-L",
            "--list-aggs",
            action="store_true",
            help="""List the available aggregate functions""",
        )

    @staticmethod
    def parse_aggy_string(argtext: str) -> Aggy:
        """
        this should replace clunky old parse_aggregate_string_arg()
        """
        rtext: str = argtext
        # extract agg_slug
        rtext, output_name = cmk_parse_delimited_str(rtext, delimiter="|", minlength=2)
        # extract agg_args
        agg_slug, agg_args = cmk_parse_delimited_str(rtext, delimiter=":", minlength=2)
        # parse any individual agg_args
        agg_args = cmk_parse_delimited_str(agg_args)

        return Aggy(agg_slug, agg_args, output_name)


class Props:
    """
    Bespoke properties
    """

    @property
    def in_column_names(self) -> list:
        """todo: make this a CMkUtil property"""
        return self.intable.column_names

    @property
    def is_empty(self) -> bool:
        """todo: make this a CMkUtil property"""
        return not self.in_column_names

    @property
    def pivot_column_name(self) -> typeOptional[str]:
        _pids = (
            cmk_parse_column_ids(
                self.args.pivot_column,
                self.in_column_names,
                column_offset=self.column_offset,
            )
            if self.args.pivot_column
            else None
        )
        if _pids and len(_pids) > 1:
            # user passed in -c/--pivot-column value containing multiple column name references
            self.argparser.error(
                f"Only one -c/--pivot-column is allowed, not {len(_pids)}: {_pids}"
            )

        pcname = self.in_column_names[_pids[0]] if _pids else None
        return pcname

    @property
    def pivot_row_ids(self) -> list:
        """
        prereqs:
         - self.in_column_names
        """
        _pids = (
            cmk_parse_column_ids(
                self.args.pivot_rows,
                self.in_column_names,
                column_offset=self.column_offset,
            )
            if self.args.pivot_rows
            else None
        )
        return _pids

    @property
    def pivot_row_names(self) -> typeOptional[list]:
        """
        prereqs:
         - self.pivot_row_ids

        """
        if self.pivot_row_ids:
            names = [self.in_column_names[i] for i in self.pivot_row_ids]
        else:
            names = None

        return names

    @property
    def aggy(self) -> Aggy:
        return self.parse_aggy_string(self.args.pivot_aggregate)

    @property
    def pivot_aggregation(self) -> agate.Aggregation:
        """specific to agate.Table.pivot argument"""
        return self.aggy.aggregation

    @property
    def pivot_title(self) -> str:
        return self.aggy.title


class CSVPivot(Props, Parser, CmkUtil):
    def print_available_aggregates(self):
        outs = self.output_file
        outs.write(f"List of aggregate functions:\n")
        for a in Aggregates.keys():
            outs.write(f"- {a}\n")

    def run(self):
        # don't bother going into main
        if self.args.list_aggs or not self.args.pivot_aggregate:
            self.print_available_aggregates()
            return

        if not self.args.pivot_rows and not self.args.pivot_column:
            self.argparser.error(
                "Either -r/--pivot-rows or -c/--pivot-column must be specified. Both cannot be left unspecified."
            )

        super().run()

    def main(self):
        if self.additional_input_expected():
            self.argparser.error("You must provide an input file or piped data.")

        self.intable: agate.Table
        outtable: agate.Table

        self.intable = agate.Table.from_csv(
            self.input_file,
            skip_lines=self.args.skip_lines,
            sniff_limit=self.args.sniff_limit,
            **self.reader_kwargs,
        )

        if self.is_empty:
            return

        # TODO: add conditional to determine whether we pivot or group by:
        # def _group_by(table: agate.Table, colnames: typeList[str]) -> agate.TableSet:
        #     for col in colnames:
        #         table = table.group_by(key=col)
        #     return table

        outtable = self.intable.pivot(
            key=self.pivot_row_names,
            pivot=self.pivot_column_name,
            aggregation=self.pivot_aggregation,
        )
        # if `pivot`/pivot_col_name isn't set, then the result is a list of row combinations
        # and a final aggregation column. We want to rename the final aggregation column,
        # e.g. from agate's default 'Count' to 'count_of'...
        #  or whatever the user has explicitly set via -a/--agg
        if not self.pivot_column_name:
            _onames = list(outtable.column_names)
            # replace the last column name in the outgoing column names
            _onames[-1] = self.pivot_title
            outtable = outtable.rename(column_names=_onames)

        outtable.to_csv(self.output_file, **self.writer_kwargs)

        return 0


def launch_new_instance():
    utility = CSVPivot()
    utility.run()


if __name__ == "__main__":
    launch_new_instance()
