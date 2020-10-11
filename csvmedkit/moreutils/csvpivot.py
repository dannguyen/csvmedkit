import csv
from collections import namedtuple
from io import StringIO
import sys
from typing import (
    List as typeList,
    NoReturn as typeNoReturn,
    Tuple as typeTuple,
    Union as typeUnion,
)

from csvmedkit import agate, slugify
from csvmedkit.aggs import Aggregates
from csvmedkit.exceptions import *
from csvmedkit.cmkutil import CmkUtil, cmk_parse_column_ids

Aggy = namedtuple("Aggy", ["agg", "agg_args", "name"], defaults=(None, None, None))


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
    def parse_aggregate_string_arg(arg: str, valid_columns: typeList[str] = []) -> Aggy:
        """
        TODO: this is ugly as heck

        `arg` looks like:
            - just the aggregate:
                'sum', 'count'
            - the aggregate, colon, comma-delimited list of arguments:
                'sum:colname' 'count:col_name,other_arg'  (only `count` has more than one arg)
            - optional pipe-separated argument for the output header name:
                'count|The Count'  'sum:colname|Summation'
        """

        def get_agg(name: str) -> typeTuple[type, str]:
            try:
                proper_name: str = name.lower()
                agg = Aggregates[proper_name]
            except KeyError as err:
                raise InvalidAggregation(
                    f'Invalid aggregation: "{name}". Call `-L/--list-aggs` to get a list of available aggregations'
                )
            else:
                return agg, proper_name

        # first we parse out the name, if specified
        argio = StringIO(arg)
        xarg, *name_arg = next(
            csv.reader(argio, delimiter="|")
        )  # _cname is either [] or ['Column Name']

        agg_name, *yarg = next(csv.reader(StringIO(xarg), delimiter=":"))
        foo, agg_proper_name = get_agg(agg_name)
        foo_args = next(csv.reader(StringIO(yarg[0]))) if yarg else []

        # if args[0] exists, assume it is a column identifier and
        # validate it
        if foo_args and valid_columns:
            if foo_args[0] not in valid_columns:
                raise ColumnIdentifierError(
                    f"Expected column name '{foo_args[0]}' to refer to a column name as an argument for {foo.__name__} aggregation. But it was not found among the list of valid column names: {valid_columns}"
                )
        # finally, we can figure out the intended output column header
        if name_arg:
            # then user specified it explicitly
            out_column_name = name_arg[0]
        else:
            out_column_name = slugify(
                f'{agg_proper_name}_of {"_".join(foo_args)}'.strip()
            )

        return Aggy(agg=foo, agg_args=foo_args, name=out_column_name)


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
    def pivot_row_names(self) -> typeUnion[list, None]:
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
    def pivot_column_name(self) -> typeUnion[str, None]:
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
    def aggregate(self) -> Aggy:
        par = self.parse_aggregate_string_arg(
            self.args.pivot_aggregate, valid_columns=self.in_column_names
        )
        return par

    @property
    def aggregate_name(self) -> str:
        return self.aggregate.name

    @property
    def pivot_aggregation(self):
        """specific to agate.Table.pivot argument"""
        p = self.aggregate
        return p.agg(*p.agg_args)


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
            _onames[-1] = self.aggregate_name
            outtable = outtable.rename(column_names=_onames)

        outtable.to_csv(self.output_file, **self.writer_kwargs)

        return 0


def launch_new_instance():
    utility = CSVPivot()
    utility.run()


if __name__ == "__main__":
    launch_new_instance()
