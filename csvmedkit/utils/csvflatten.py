#!/usr/bin/env python

from csvmedkit import agate
from csvmedkit.cmk.cmkutil import CmkUtil, UniformReader
from shutil import get_terminal_size
import sys
import textwrap
from typing import (
    Callable as CallableType,
    Optional as OptionalType,
)

DEFAULT_EOR_MARKER = "="
DEFAULT_MAX_LENGTH = 50
FLAT_COLUMN_NAMES = (
    "field",
    "value",
)
REC_ID_COLUMN_NAME = "recid"

COLTYPE_MAP = {
    REC_ID_COLUMN_NAME: agate.Number(),
    "field": agate.Text(null_values=()),
    "value": agate.Text(null_values=()),
}

FLAT_COL_PADDING = 4
FLAT_COL_WIDTH = len("field") + FLAT_COL_PADDING


class CSVFlatten(UniformReader, CmkUtil):
    description = """Prints flattened records, such that each row represents a record's fieldname and corresponding value,
                     similar to transposing a record in spreadsheet format"""

    override_flags = ["l"]

    def add_arguments(self):

        self.argparser.add_argument(
            "-c",
            "--csv",
            dest="csvify",
            action="store_true",
            help="""Print output in CSV format""",
        )

        self.argparser.add_argument(
            "-L",
            "--max-length",
            dest="max_field_length",
            metavar="<max_length_of_field>",
            type=int,
            help="""Split up values longer than <max_length_of_field> into multiple row-values as needed.""",
        )

        self.argparser.add_argument(
            "-R",
            "--rec-id",
            dest="rec_ids_mode",
            action="store_true",
            help="""Include a `recid` column at the beginning of each row, corresponding to the
            numerical index of a flatten record.

            (Using this option disables the default record separator, but you can still set --separator
            to a custom marker)
            """,
        )

        self.argparser.add_argument(
            "-B",
            "--label-chunks",
            dest="label_chunks_mode",
            action="store_true",
            help="""When a long value is split into multiple "chunks", the `field` (i.e. first column) is left blank after the first chunk.
                    Setting the --label-chunks flag will fill the `field` column with: "field~n", where `n` indicates the n-th chunk of a chopped value""",
        )

        self.argparser.add_argument(
            "-N",
            "--newline-sep",
            dest="newline_separator",
            action="store_true",
            help="""Separate each flattened record with a blank newline. Cannot be used with -S/--s""",
        )

        self.argparser.add_argument(
            "-S",
            "--separator",
            dest="record_separator",
            metavar="TEXT_MARKER",
            type=str,
            help=f"""Separate each flatten record with a blank row in which the `field` column contains a
                text marker. The default marker is a series of "{DEFAULT_EOR_MARKER}". Set this option to "" or "none"
                to disable.""",
        )

    @property
    def chunkpattern(self) -> CallableType:
        """
        expects self.max_field_length to be set
        """
        # if max_field_length is specified, then the pattern for chunking uses it
        if self.max_field_length:
            _cp = lambda txt: textwrap.wrap(txt, width=self.max_field_length)
        else:  # we just split newlines
            _cp = lambda txt: txt.splitlines()
        return _cp

    @property
    def record_separator(self) -> OptionalType[str]:
        """
        preconditions:
            - self.max_column_name_length
            - self.rec_ids_mode
        """
        marker: OptionalType[str]
        if self.args.newline_separator:
            # empty string effectively makes a blank row
            marker = ""
        else:
            argval = self.args.record_separator
            if argval == "none" or argval == "":
                # user explicitly disables it
                marker = None
            elif argval:
                # user specified *something*
                marker = argval
            else:
                # user did not set option
                if self.rec_ids_mode:
                    # if we're using rec_ids, record separation is disabled by default
                    marker = None
                else:
                    # this is the default record separator
                    marker = "".join(
                        DEFAULT_EOR_MARKER for i in range(self.max_column_name_length)
                    )

        return marker

    @property
    def label_chunks_mode(self):
        return self.args.label_chunks_mode

    @property
    def rec_ids_mode(self):
        return self.args.rec_ids_mode

    @property
    def csvify(self):
        return self.args.csvify

    def read_input(self):
        self._rows = agate.csv.reader(self.skip_lines(), **self.reader_kwargs)
        self._column_names = next(self._rows)
        self._read_input_done = True

    def main(self):
        if self.args.newline_separator and self.args.record_separator:
            self.argparser.error("Cannot set both -N/--newline-sep and -S/--separator.")

        if self.additional_input_expected():
            self.argparser.error("You must provide an input file or piped data.")

        # UniformReader (DRY later)
        self.read_input()
        if self.is_empty:
            return
        # /UniformReader

        outrows: list
        outtable: agate.Table

        self.output_flat_column_names = (
            FLAT_COLUMN_NAMES
            if not self.rec_ids_mode
            else (REC_ID_COLUMN_NAME,) + FLAT_COLUMN_NAMES
        )

        self.max_column_name_length = max(
            len(c) for c in (self.i_column_names + list(self.output_flat_column_names))
        )

        if (
            self.args.max_field_length or self.args.max_field_length == 0
        ):  # 0 is considered to be infinite/no-wrap
            self.max_field_length = self.args.max_field_length
        elif not self.csvify and not self.args.max_field_length:
            # user wants it pretty but didn't specify a max_field_length, so we automatically figure it out
            # TODO: this is ugly
            termwidth = get_terminal_size().columns
            flatcol_widths = FLAT_COL_WIDTH * (len(self.output_flat_column_names) - 1)
            avail_width = termwidth - (
                flatcol_widths + self.max_column_name_length + FLAT_COL_PADDING
            )
            self.max_field_length = (
                avail_width if avail_width > FLAT_COL_PADDING else DEFAULT_MAX_LENGTH
            )
        else:
            self.max_field_length = None

        outrows = []
        for row_idx, row in enumerate(self.i_rows):
            # TODO: wtf is this spagehtti:
            o_row = (
                [
                    row_idx,
                ]
                if self.rec_ids_mode
                else []
            )

            if self.record_separator is not None and row_idx > 0:
                # print out a record-separator
                sep = [None] if self.rec_ids_mode else []
                outrows.append(sep + [self.record_separator, None])

            for col_idx, colname in enumerate(self.i_column_names):
                # value_lines = row[col_idx].strip().splitlines()
                # for line in value_lines:
                txt = row[col_idx].strip()
                chunks = self.chunkpattern(txt) or [""]
                for chunk_idx, chunk in enumerate(chunks):
                    if chunk_idx == 0:
                        fieldname = colname
                    else:
                        fieldname = (
                            f"{colname}__{chunk_idx}"
                            if self.label_chunks_mode is True
                            else None
                        )
                    outrows.append(o_row + [fieldname, chunk])

        if self.csvify:
            writer = agate.csv.writer(self.output_file, **self.writer_kwargs)
            writer.writerow(self.output_flat_column_names)
            writer.writerows(outrows)

        else:
            outtable = agate.Table(
                outrows,
                column_names=self.output_flat_column_names,
                column_types={k: COLTYPE_MAP[k] for k in self.output_flat_column_names},
            )

            outtable.print_table(
                output=self.output_file,
                max_column_width=None,
                max_rows=None,
                max_columns=None,
            )


def launch_new_instance():
    utility = CSVFlatten()
    utility.run()


if __name__ == "__main__":
    launch_new_instance()
