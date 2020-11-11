# import csv
# from io import StringIO
# import itertools
from collections import deque
from math import inf as INFINITY
from typing import (
    List as ListType,
    NoReturn as NoReturnType,
    Optional as OptionalType,
    Sequence as SequenceType,
    Union as UnionType,
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
            "--indexes",
            dest="indexes",
            metavar="<values>",
            type=str,
            help="""Comma-delimited string of indexes to include. Can be individual indexes and ranges, e.g. '0' or '0-6,12', or '0-6,12-'""",
        )

        self.argparser.add_argument(
            "--head",
            dest="head",
            metavar="<n>",
            type=int,
            help="""Return the header and the first <n> rows""",
        )

        self.argparser.add_argument(
            "--tail",
            dest="tail",
            metavar="<n>",
            type=int,
            help="""Return the header and the last <n> rows""",
        )

    def calculate_slice_ranges(self) -> NoReturnType:
        # TODO: this is ugly spaghetti but it works
        self.slice_ranges: ListType[SequenceType]
        self.slice_lower_bound: UnionType[
            int, float
        ] = INFINITY  # type float is allowed because INFINITY is a float

        indexes = []
        intervals = []

        for txt in cmk_parse_delimited_str(self.included_indexes):
            rtxt = re.sub(r"\s+", "", txt).strip()
            if not re.match(r"^(?:\d+|\d+-|\d+-\d+)$", rtxt):
                raise IncorrectlyFormattedString(
                    f"Your --indexes argument, '{self.included_indexes}', has an incorrectly formatted value: '{txt}'"
                )

            if "-" not in rtxt:
                # just a regular index
                indexes.append(int(rtxt))
            else:
                # todo: this could be really cleaned up
                i_start, i_end = rtxt.split("-")
                i_start = int(i_start)
                i_end = None if i_end == "" else int(i_end)
                if i_end is None:
                    # implicitly, there is an i_start, even if it's 0
                    # interpret '9-' as '9 and everything bigger'
                    self.slice_lower_bound = min(self.slice_lower_bound, i_start)
                else:
                    # implicitly, i_start and i_end are both there
                    if i_end < i_start:
                        raise InvalidRange(f"Invalid range specified: {rtxt}")
                    else:
                        intervals.append(range(i_start, i_end + 1))

        self.slice_ranges = [sorted(indexes)] + intervals

    @property
    def head_count(self) -> int:
        return self.args.head

    @property
    def tail_count(self) -> int:
        return self.args.tail

    @property
    def included_indexes(self) -> str:
        return self.args.indexes

    def read_input(self):
        self._rows = agate.csv.reader(self.skip_lines(), **self.reader_kwargs)
        self._column_names = next(self._rows)
        self._read_input_done = True

    def select_mode(self) -> str:
        """
        besides figuring out which if the 3 mutually exclusive modes is activated, additional
        argument validation is done here.
        """
        modes = [
            k
            for k in (
                "indexes",
                "head",
                "tail",
            )
            if getattr(self.args, k) is not None
        ]

        if not modes:
            self.argparser.error(
                "At least one of the following options must be included: --indexes, --head, or --tail"
            )
        elif len(modes) > 1:
            errtxt = ", ".join(f"--{m}" for m in modes)
            self.argparser.error(
                f"You specified options {errtxt}. But only one of these options can be used at a time."
            )
        else:
            pass  # this shouldn't happen

        mode = modes[0]
        if mode == "head" or mode == "tail":
            mcount = getattr(self, f"{mode}_count")
            if mcount <= 0:
                self.argparser.error(
                    f"The value for --{mode} must be greater than 0, not {mcount}"
                )

        return mode

    def main(self):
        if self.additional_input_expected():
            self.argparser.error("You must provide an input file or piped data.")

        self.read_input()
        if self.is_empty:
            return

        writer = agate.csv.writer(self.output_file, **self.writer_kwargs)
        writer.writerow(self.i_column_names)
        mode = self.select_mode()

        if mode == "indexes":
            self.calculate_slice_ranges()
            for i, row in enumerate(self.i_rows):
                if i >= self.slice_lower_bound or any(
                    i in r for r in self.slice_ranges
                ):
                    writer.writerow(row)
        elif mode == "head":
            for i, row in enumerate(self.i_rows, 1):
                if i > self.head_count:
                    break
                writer.writerow(row)

        elif mode == "tail":
            tdata = deque(maxlen=self.tail_count)
            for row in self.i_rows:
                tdata.append(row)
            writer.writerows(tdata)

    def run(self):
        self.input_file = self._open_input_file(self.args.input_path)
        super().run()


def launch_new_instance():
    utility = CSVSlice()
    utility.run()


if __name__ == "__main__":
    launch_new_instance()
