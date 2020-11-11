from argparse import _AppendAction as argAppendAction, _copy_items as arg_copy_items
import csv
from collections import namedtuple
from io import StringIO
import sys
from typing import (
    List as ListType,
    NoReturn as NoReturnType,
    Tuple as TupleType,
    Optional as OptionalType,
)

from csvmedkit import agate
from csvmedkit.exceptions import *
from csvmedkit.cmk.aggs import Aggy, Aggregates
from csvmedkit.cmk.cmkutil import CmkUtil, UniformReader
from csvmedkit.cmk.helpers import cmk_parse_column_ids, cmk_parse_delimited_str


class AppendAggyAction(argAppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        aggy = Aggy.parse_aggy_string(values)
        super().__call__(parser, namespace, aggy, option_string)


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

        ################# unique arguments

        self.argparser.add_argument(
            "--list-aggs",
            action="store_true",
            help="""List the available aggregate functions""",
        )

        self.argparser.add_argument(
            "-r",
            "--pivot-rows",
            dest="pivot_rownames",
            type=str,
            help="""The column name(s) on which to use as pivot rows. Should be either one name
                                    (or index) or a comma-separated list with one name (or index)""",
        )

        self.argparser.add_argument(
            "-c",
            "--pivot-column",
            dest="pivot_colname",
            type=str,
            help="Optionally, a column name/id to use as a pivot column. Only one is allowed",
        )

        self.argparser.add_argument(
            "-a",
            "--agg",
            action=AppendAggyAction,
            dest="aggregates_list",
            help="""The name of an aggregation to perform on each group of data in the pivot table.
                                    For aggregations that require an argument (i.e. a column name), pass in the aggregation name,
                                    followed by a colon, followed by comma-delimited arguments,
                                     e.g. `-a "sum:age"` and `-a "count:name,hello"

                                    To see a list, run `csvpivot --list-aggs`
                                    """,
        )


class Props:
    """
    Bespoke properties
    """

    @property
    def pivot_column_name(self) -> OptionalType[str]:

        if self.args.pivot_colname:
            cids = cmk_parse_column_ids(
                self.args.pivot_colname,
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
    def pivot_row_ids(self) -> ListType:
        if self.args.pivot_rownames:
            return cmk_parse_column_ids(
                self.args.pivot_rownames,
                self.i_column_names,
                column_offset=self.column_offset,
            )
        else:
            return []

    @property
    def pivot_row_names(self) -> ListType:
        """
        prereqs:
         - self.pivot_row_ids
        """
        if self.pivot_row_ids:
            return [self.i_column_names[i] for i in self.pivot_row_ids]
        else:
            return []


class CSVPivot(UniformReader, Props, Parser, CmkUtil):
    def _validate_aggy_column_arguments(
        self, aggy: Aggy, table: agate.Table
    ) -> NoReturnType:
        """
        Aggy is csvpivot/agate.Table agnostic, so this method:

        - makes sure that aggy's ostensible column_name argument is actually in the table
        - typecasts the second argument of count() to match the datatype of the column that it counts

        """

        ############################
        # checking valid column name
        # (For now, all possible Aggregates use the first argument (if it exists) as the column_name to aggregate)
        if aggy._args:
            _col = aggy._args[0]
            # the following is redundant with the filter_rows() check already done
            if _col not in table.column_names:
                raise ColumnNameError(
                    "ColumnNameError: "
                    + f"Attempted to perform `{aggy.slug}('{_col}', ...)`. "
                    + f"But '{_col}' was expected to be a valid column name, i.e. from: {table.column_names}",
                )

        ################################################################
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

    def _filter_input_rows(
        self, rows: agate.csv.DictReader, colnames: ListType[str]
    ) -> agate.Table:
        """
        trim self.i_rows to the actually used columns
        """
        # trim self.intable to the relevant, i.e. actually used columns
        # TODO: clean this ugliness up
        used_cols: list = self.pivot_row_names or []
        if self.pivot_column_name:
            used_cols.append(self.pivot_column_name)
        if self.args.aggregates_list:
            used_cols.extend(
                [a.column_name for a in self.args.aggregates_list if a.column_name]
            )

        for c in list(set(used_cols)):
            if not c in colnames:
                raise ColumnNameError(
                    f"'{c}' is not a valid column name; column names are: {colnames}"
                )

        with StringIO() as ftxt:
            fd = csv.DictWriter(ftxt, fieldnames=used_cols)
            fd.writeheader()

            for row in rows:
                fd.writerow({c: row[c] for c in used_cols})

            ftxt.seek(0)
            table = agate.Table.from_csv(
                ftxt,
                skip_lines=self.args.skip_lines,
                sniff_limit=self.args.sniff_limit,
                column_types=self.get_column_types(),
                **self.reader_kwargs,
            )
        return table

    def read_input(self):
        self._rows = agate.csv.DictReader(self.skip_lines(), **self.reader_kwargs)
        self._column_names = self._rows.fieldnames
        self._read_input_done = True

    def print_available_aggregates(self):
        outs = self.output_file
        outs.write(f"List of aggregate functions:\n")
        for a in Aggregates.keys():
            outs.write(f"- {a}\n")

    def main(self):
        if self.additional_input_expected():
            self.argparser.error("You must provide an input file or piped data.")

        # UniformReader (DRY later)
        self.read_input()
        if self.is_empty:
            return
        # TODO ugly access of internal variables, DRY later:
        self._rows = self._filter_input_rows(self.i_rows, self.i_column_names)
        self._column_names = self.i_rows.column_names

        # extract aggies
        aggies: list
        if not self.args.aggregates_list:
            # set default aggregation if there were none
            aggies = [Aggy.parse_aggy_string("count")]
        else:
            aggies = self.args.aggregates_list.copy()

        for a in aggies:
            self._validate_aggy_column_arguments(a, table=self.i_rows)

        outtable: agate.Table
        outtable = self.i_rows

        if self.pivot_column_name:
            # in this mode, only one aggregation is allowed. This is enforced inside run()
            # Also, this aggregation:
            # - is performed for each group i.e. cell of the aggregated data
            # - aggy.title is not used and thus ignored
            #   - TODO: warn user that title is ignored?
            outtable = outtable.pivot(
                key=self.pivot_row_names or None,
                pivot=self.pivot_column_name or None,
                aggregation=aggies[0].aggregation,
            )
        else:
            # user wants multiple aggregations for rows, so this is essentially a group_by
            for rcol in self.pivot_row_names:
                outtable = outtable.group_by(key=rcol)

            outtable = outtable.aggregate([(a.title, a.aggregation) for a in aggies])

        outtable.to_csv(self.output_file, **self.writer_kwargs)
        return 0

    def run(self):
        # don't bother going into main
        if self.args.list_aggs or (
            self.args.aggregates_list and self.args.aggregates_list[0] == ""
        ):
            self.print_available_aggregates()
            return

        if not self.args.pivot_rownames and not self.args.pivot_colname:
            self.argparser.error(
                "Either -r/--pivot-rows or -c/--pivot-column must be specified. Both cannot be left unspecified."
            )

        if self.args.pivot_colname and (
            self.args.aggregates_list and len(self.args.aggregates_list) > 1
        ):
            self.argparser.error(
                f"""Cannot specify --pivot-column '{self.pivot_column_name}' and have more than one aggregation; you specified {len(self.args.aggregates_list)}: {self.args.aggregates_list}"""
            )

        super().run()


def launch_new_instance():
    utility = CSVPivot()
    utility.run()


if __name__ == "__main__":
    launch_new_instance()
