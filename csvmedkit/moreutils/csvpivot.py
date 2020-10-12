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
from csvmedkit.exceptions import *
from csvmedkit.cmk.aggs import Aggy, Aggregates
from csvmedkit.cmk.cmkutil import CmkUtil, UniformReader
from csvmedkit.cmk.helpers import cmk_parse_column_ids, cmk_parse_delimited_str


class Parser:
    """
    Functionality related to command-line configuration and argument handling
    """

    description = """Do a simple pivot table, by row, column, or row and column"""
    override_flags = ["l"]

    def add_arguments(self):

        self.argparser.add_argument(
            "--date-format",
            dest="date_format",
            help='Specify a strptime date format string like "%%m/%%d/%%Y".',
        )
        self.argparser.add_argument(
            "--datetime-format",
            dest="datetime_format",
            help='Specify a strptime datetime format string like "%%m/%%d/%%Y %%I:%%M %%p".',
        )

        self.argparser.add_argument(
            "-L",
            "--locale",
            dest="locale",
            default="en_US",
            help="Specify the locale (en_US) of any formatted numbers.",
        )

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
            action="append",
            dest="aggregates_list",
            # dest="pivot_aggregate",
            # type=str,
            help="""The name of an aggregation to perform on each group of data in the pivot table.
                                    For aggregations that require an argument (i.e. a column name), pass in the aggregation name,
                                    followed by a colon, followed by comma-delimited arguments,
                                     e.g. `-a "sum:age"` and `-a "count:name,hello"

                                    To see a list, run `csvpivot --list-aggs`
                                    """,
        )

        self.argparser.add_argument(
            "--list-aggs",
            action="store_true",
            help="""List the available aggregate functions""",
        )


class Props:
    """
    Bespoke properties
    """

    @property
    def intable(self) -> agate.Table:
        """same as i_rows, just a better name specific to this command, which uses agate.Table"""
        return self.i_rows

    @property
    def pivot_column_name(self) -> typeOptional[str]:

        if self.args.pivot_column:
            cids = cmk_parse_column_ids(
                self.args.pivot_column,
                self.i_column_names,
                column_offset=self.column_offset,
            )
        else:
            cids = None

        if cids and len(cids) > 1:
            # user passed in -c/--pivot-column value containing multiple column name references
            self.argparser.error(
                f"Only one -c/--pivot-column is allowed, not {len(cids)}: {cids}"
            )

        return self.i_column_names[cids[0]] if cids else None

    @property
    def pivot_row_ids(self) -> typeOptional[list]:
        if self.args.pivot_rows:
            c = cmk_parse_column_ids(
                self.args.pivot_rows,
                self.i_column_names,
                column_offset=self.column_offset,
            )
        else:
            c = None
        return c

    @property
    def pivot_row_names(self) -> typeOptional[list]:
        """
        prereqs:
         - self.pivot_row_ids
        """
        if self.pivot_row_ids:
            names = [self.i_column_names[i] for i in self.pivot_row_ids]
        else:
            names = None
        return names


class CSVPivot(UniformReader, Props, Parser, CmkUtil):
    def print_available_aggregates(self):
        outs = self.output_file
        outs.write(f"List of aggregate functions:\n")
        for a in Aggregates.keys():
            outs.write(f"- {a}\n")

    def run(self):
        # don't bother going into main
        if self.args.list_aggs or (
            self.args.aggregates_list and self.args.aggregates_list[0] == ""
        ):
            self.print_available_aggregates()
            return

        if not self.args.pivot_rows and not self.args.pivot_column:
            self.argparser.error(
                "Either -r/--pivot-rows or -c/--pivot-column must be specified. Both cannot be left unspecified."
            )

        if self.args.pivot_column and (
            self.args.aggregates_list and len(self.args.aggregates_list) > 1
        ):
            self.argparser.error(
                f"""Cannot specify --pivot-column '{self.pivot_column_name}' and have more than one aggregation; you specified {len(self.args.aggregates_list)}: {self.args.aggregates_list}"""
            )

        super().run()

    def validate_aggy_column_arguments(self, aggy: Aggy):
        """
        Aggy is csvpivot/agate.Table agnostic, so this method:

        - makes sure that aggy's ostensible column_name argument is actually in the table
        - typecasts the second argument of count() to match the datatype of the column that it counts

        """
        table = self.intable

        ############################
        # checking valid column name
        # (For now, all possible Aggregates use the first argument (if it exists) as the column_name to aggregate)
        if aggy._args:
            _col = aggy._args[0]
            if _col not in table.column_names:
                raise InvalidAggregationArgument(
                    "InvalidAggregationArgument: "
                    + f"Attempted to perform `{aggy.slug}('{_col}', ...)`. "
                    + f"But '{_col}' was expected to be a valid column name, i.e. from: {table.column_names}",
                )

        ############################
        # if the aggregation is count(), and there are 2 arguments
        #   then the 2nd argument is typecasted against the table.column
        #   (i.e. the column name referenced by the first arg)
        if len(aggy._args) > 1 and aggy.slug == "count":
            col_name, cval = aggy.agg_args[0:2]

            try:
                # get column from first arg, which is presumably a column_name
                _col: agate.Column = next(
                    c for c in table.columns if c.name == col_name
                )
            except StopIteration as err:
                raise ColumnIdentifierError(
                    f"'{col_name}' – from `{argtext}` – is expected to be a column name, but it was not found in the table: {table.column_names}"
                )
            else:
                dtype = _col.data_type

            # attempt a data_type conversion
            try:
                dval = dtype.cast(cval)
                # modify agg_args
            except agate.CastError as err:
                typename: str = type(dtype).__name__
                raise agate.CastError(
                    f"You attempted to count '{cval}' in column '{col_name}', which has datatype {typename}. But '{cval}' could not be converted to {typename}."
                )
            else:
                aggy._args[1] = dval

    def read_input(self):
        self._rows = agate.Table.from_csv(
            self.input_file,
            skip_lines=self.args.skip_lines,
            sniff_limit=self.args.sniff_limit,
            column_types=self.get_column_types(),
            **self.reader_kwargs,
        )
        self._column_names = self._rows.column_names
        self._read_input_done = True

    def main(self):
        if self.additional_input_expected():
            self.argparser.error("You must provide an input file or piped data.")

        # UniformReader (DRY later)
        self.read_input()
        if self.is_empty:
            return

        if not self.args.aggregates_list:
            aggtextlist = ["count"]
        else:
            aggtextlist = self.args.aggregates_list.copy()

        self.aggies: list = []
        for txt in aggtextlist:
            aggy = Aggy.parse_aggy_string(txt)
            self.validate_aggy_column_arguments(aggy)
            self.aggies.append(aggy)

        if self.pivot_column_name:
            # in this mode, only one aggregation is allowed. This is enforced inside run()
            # Also, this aggregation:
            # - is performed for each group i.e. cell of the aggregated data
            # - aggy.title is not used and thus ignored
            #   - TODO: warn user that title is ignored?

            aggy: Aggy = self.aggies[0]
            pivot_aggregation: agate.Aggregation = aggy.aggregation

            outtable: agate.Table
            outtable = self.i_rows.pivot(
                key=self.pivot_row_names,
                pivot=self.pivot_column_name,
                aggregation=pivot_aggregation,
            )
            # if `pivot`/pivot_col_name isn't set, then the result is a list of row combinations
            # and a final aggregation column. We want to rename the final aggregation column,
            # e.g. from agate's default 'Count' to 'count_of'...
            #  or whatever the user has explicitly set via -a/--agg
            if not self.pivot_column_name:
                _onames = list(outtable.column_names)
                # replace the last column name in the outgoing column names
                _onames[-1] = pivot_title
                outtable = outtable.rename(column_names=_onames)

        else:
            # user wants multiple aggregations for rows, so this is essentially a groupby

            # throw error on:             if not self.pivot_column_name:
            outtable: agate.Table
            outtable = self.intable
            for rcol in self.pivot_row_names:
                outtable = outtable.group_by(key=rcol)

            outtable = outtable.aggregate(
                [(a.title, a.aggregation) for a in self.aggies]
            )

        outtable.to_csv(self.output_file, **self.writer_kwargs)

        return 0


def launch_new_instance():
    utility = CSVPivot()
    utility.run()


if __name__ == "__main__":
    launch_new_instance()
