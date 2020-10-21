# import csv
# from io import StringIO
# import itertools
from math import inf as INFINITY
from typing import (
    List as typeList,
    NoReturn as typeNoReturn,
    Optional as typeOptional,
    Sequence as typeSequence,
    Union as typeUnion,
)

from csvmedkit import agate, re_std as re
from csvmedkit.exceptions import IncorrectlyFormattedString, InvalidRange
from csvmedkit.cmk.cmkutil import CmkMixedUtil, UniformReader
from csvmedkit.cmk.helpers import cmk_parse_delimited_str


class CSVSlice(UniformReader, CmkMixedUtil):
    description = """Returns the dataset's header and any rows in the specified 0-index inclusive ranges"""
    override_flags = [
        "L",
    ]

    def add_arguments(self):

        self.argparser.add_argument(
            "-i",
            "--intervals",
            dest="slice_ranges_str",
            metavar="<intervals>",
            required=True,
            type=str,
            help="""Comma-delimited string of intervals to slice, including individual indexes and ranges, e.g. '0' or '0-6,12', or '0-6,12-'""",
        )

    def calculate_slice_ranges(self) -> typeNoReturn:
        self.slice_ranges: typeList[typeSequence]
        self.slice_lower_bound: typeUnion[
            int, float
        ] = INFINITY  # type float is allowed because INFINITY is a float

        indexes = []
        intervals = []

        for txt in cmk_parse_delimited_str(self.args.slice_ranges_str):
            rtxt = re.sub(r"\s+", "", txt).strip()
            if not re.match(r"^(?:\d+|\d+-|\d+-\d+)$", rtxt):
                raise IncorrectlyFormattedString(
                    f"Your --intervals argument, '{self.args.slice_ranges_str}', has an incorrectly formatted value: '{txt}'"
                )

            if "-" not in rtxt:
                # just a regular index
                indexes.append(int(rtxt))
            else:
                i_start, i_end = [int(i) if i else 0 for i in rtxt.split("-")]
                if i_start and i_end:
                    if i_end <= i_start:
                        raise InvalidRange(f"Invalid range specified: {rtxt}")
                    else:
                        intervals.append(range(i_start, i_end + 1))
                elif i_end:
                    # interpret '-42' as: everything from 0 to 42
                    intervals.append(range(0, i_end + 1))
                elif i_start:
                    # interpret '9-' as '9 and everything bigger'
                    self.slice_lower_bound = min(self.slice_lower_bound, i_start)

        self.slice_ranges = [sorted(indexes)] + intervals

    def read_input(self):
        self._rows = agate.csv.reader(self.skip_lines(), **self.reader_kwargs)
        self._column_names = next(self._rows)
        self._read_input_done = True

    def main(self):
        if self.additional_input_expected():
            self.argparser.error("You must provide an input file or piped data.")

        self.read_input()
        if self.is_empty:
            return

        self.calculate_slice_ranges()

        writer = agate.csv.writer(self.output_file, **self.writer_kwargs)
        writer.writerow(self.i_column_names)

        for i, row in enumerate(self.i_rows):
            if i >= self.slice_lower_bound or any(i in r for r in self.slice_ranges):
                writer.writerow(row)

    def run(self):
        self.input_file = self._open_input_file(self.args.input_path)
        super().run()


def launch_new_instance():
    utility = CSVSlice()
    utility.run()


if __name__ == "__main__":
    launch_new_instance()
