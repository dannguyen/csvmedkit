#!/usr/bin/env python

import agate

from csvmedkit.kit.cmkutil import CmkUtil
from csvmedkit import rxlib as re
import os
import sys

from typing import NoReturn as typeNoReturn

DEFAULT_CHOP_LENGTH = 50
DEFAULT_EOR_MARKER = "~"
FLAT_COLUMN_NAMES = (
    "field",
    "value",
)
PRETTIFY_PADDING = 15


class CSVFlatten(CmkUtil):
    description = """Prints flattened records, such that each row represents a record's fieldname and corresponding value,
                     similar to transposing a record in spreadsheet format"""

    override_flags = ["l"]

    def add_arguments(self):
        self.argparser.add_argument(
            "-L",
            "--chop-length",
            dest="chop_length",
            type=int,
            help="""Chop up values to fit this length; longer values are split into multiple rows,
                                             e.g. for easier viewing when using -P/--prettify""",
        )

        self.argparser.add_argument(
            "-B",
            "--chop-labels",
            dest="label_chopped_values",
            action="store_true",
            help="""When a value is chopped into multiple rows, the `fieldname` (i.e. first column)
                                            is left blank after the first chop/row. Setting the --X-label flag
                                            will fill the `fieldname` column with: "fieldname~n", where `n` indicates
                                            the n-th row of a chopped value""",
        )

        self.argparser.add_argument(
            "-E",
            "--eor",
            dest="end_of_record_marker",
            type=str,
            help="""end of record; When flattening multiple records, separate each records with
                                            a row w/ fieldname of [marker]. Set to '' or 'none' to disable""",
        )

        self.argparser.add_argument(
            "-P",
            "--prettify",
            dest="prettify",
            action="store_true",
            help="""Print output in tabular format instead of CSV""",
        )

    def _extract_csv_writer_kwargs(self) -> dict:
        """
        we force arg.out_quoting to be 1 i.e. Quote All
        """
        if self.args.chop_length:
            return {"quoting": 1}
        else:
            return {}

    def main(self):
        if self.additional_input_expected():
            self.argparser.error("You must provide an input file or piped data.")

        # the following args are referenced in self.reader_kwargs and used in get_rows_and_column_names_and_column_ids
        rows = self.text_csv_reader()
        column_names = next(rows)

        self.max_column_name_len = (
            max(len(c) for c in column_names) if column_names else 0
        )

        self.prettify = True if self.args.prettify else False
        if self.args.chop_length:
            self.chop_length = self.args.chop_length
        elif self.prettify and not self.args.chop_length:
            # user wants it pretty but didn't specify a chop_length, so we automatically figure it out
            tsize = os.get_terminal_size()
            self.chop_length = tsize.columns - (
                self.max_column_name_len + PRETTIFY_PADDING
            )
        else:
            self.chop_length = None

        if self.args.label_chopped_values and not self.chop_length:
            self.argparser.error(
                '"-B/--chop-label is an invalid option unless -L/--chop-length is specified'
            )

        _eor = self.args.end_of_record_marker
        if _eor == "none" or _eor == "":
            self.end_of_record_marker = None
        elif _eor:  # use default
            self.end_of_record_marker = _eor
        else:
            self.end_of_record_marker = "".join(
                DEFAULT_EOR_MARKER for i in range(self.max_column_name_len)
            )

        # if chop_length is specified, then the pattern for chunking uses it
        if self.chop_length:
            self.chunkpattern = re.compile(fr"[^\n]{{1,{self.chop_length}}}")
        else:
            self.chunkpattern = re.compile(r".+")

        outrows = []

        for i, row in enumerate(rows):
            if self.end_of_record_marker and i > 0:
                # a "normal" fieldname/value row, in which value is less than maxcolwidth
                outrows.append(
                    (
                        self.end_of_record_marker,
                        None,
                    )
                )

            for j, colname in enumerate(column_names):
                value_lines = row[j].strip().splitlines()
                chunkcount = 0
                for line in value_lines:
                    if not line:  # i.e. a blank new line
                        chunkcount += 1
                        fieldname = (
                            f"{colname}_{chunkcount}"
                            if self.args.label_chopped_values is True
                            else None
                        )
                        outrows.append(
                            (
                                fieldname,
                                "",
                            )
                        )
                    else:
                        chunks = self.chunkpattern.findall(line)
                        for k, chunk in enumerate(chunks):
                            if chunkcount == 0:
                                fieldname = colname
                            else:
                                fieldname = (
                                    f"{colname}__{chunkcount}"
                                    if self.args.label_chopped_values is True
                                    else None
                                )
                            chunkcount += 1
                            outrows.append(
                                (
                                    fieldname,
                                    chunk,
                                )
                            )

        if self.args.prettify:
            outtable = agate.Table(outrows, column_names=FLAT_COLUMN_NAMES)
            outtable.print_table(max_column_width=None, max_rows=None, max_columns=None)
        else:
            writer = agate.csv.writer(self.output_file, **self.writer_kwargs)
            writer.writerow(FLAT_COLUMN_NAMES)
            writer.writerows(outrows)


def launch_new_instance():
    utility = CSVFlatten()
    utility.run()


if __name__ == "__main__":
    launch_new_instance()
