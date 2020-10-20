import csv
from io import StringIO
import itertools
from typing import (
    List as typeList,
    Iterable as typeIterable,
    NoReturn as typeNoReturn,
    Tuple as typeTuple,
)

from csvmedkit import re_plus as re
from csvmedkit.cmk.cmkutil import CmkUtil
from csvmedkit.cmk.helpers import cmk_parse_column_ids, cmk_slugify


class CSVHeader(CmkUtil):
    description = """Prints flattened records, such that each row represents a record's fieldname and corresponding value,
                     similar to transposing a record in spreadsheet format"""

    override_flags = [
        "l",
        "H",
    ]

    def add_arguments(self):
        self.argparser.add_argument(
            "--AH",
            "--add-header",
            dest="add_header",
            action="store_true",
            help="""Given a dataset with no header, this flag adds generic fieldnames for each column, numbered starting from 1, e.g. field_1, field_2, and so on.""",
        )

        self.argparser.add_argument(
            "--ZH",
            "--zap-header",
            dest="zap_header",
            action="store_true",
            help="""Similar to `--HA/--add-headers`, but instead of adding a generic header row, completely replace (i.e. "zap") the current headers""",
        )

        self.argparser.add_argument(
            "-R",
            "--rename",
            dest="rename_headers",
            metavar="<renamed_column_pairs>",
            type=str,
            help="""Rename individual columns. The required argument is a comma-delimited string of pipe-delimited pairs — column id/name and the new name.

            For example, to rename the "a" column to "Apples"; and also, the 2nd and 3rd columns to "hello" and "world", respectively, the quoted argument string would be:

                'a|Apples,2|hello,3|world'
            """,
        )

        self.argparser.add_argument(
            "-S",
            "--slugify",
            dest="slugify_mode",
            action="store_true",
            help="""Converts the existing column names to snake_case style. For example, APPLES and 'Date - Time ' are converted, respectively, to 'apples' and 'date_time'""",
        )

        self.argparser.add_argument(
            "-X",
            "--regex",
            dest="regex_headers",
            nargs=2,
            metavar="<arg>",
            type=str,
            help="""In the existing column names, replace all occurrences of a regular expression <pattern> (1st arg) with <replacement> (2nd arg).""",
        )

        self.argparser.add_argument(
            "-P",
            "--preview",
            action="store_true",
            help="""When no options are invoked, only the existing header is printed as a comma-delimited list. Invoking any of the aforementioned options prints the transformed header and the data. In the latter case, use the --preview flag to see only what the transformed headers look like.""",
        )

    @property
    def add_header(self) -> bool:
        return self.args.add_header

    @property
    def zap_header(self) -> bool:
        return self.args.zap_header

    @property
    def preview(self) -> bool:
        return self.args.preview

    @property
    def slugify_mode(self) -> bool:
        return self.args.slugify_mode

    @staticmethod
    def parse_rename_param(
        txt: str,
        column_names: typeList[str],
    ) -> typeList[typeTuple[str]]:
        """
        Converts:
          'a|apples,b|Be Bee,"c|Sea, shell "'
        to:
          [('a', 'apples'), ('b', 'Be Bee'), ('c', 'Sea, shell ')]

        Doesn't validate against self.column_names or any other conversions

        """
        return [h.split("|") for h in next(csv.reader(StringIO(txt)))]

    def output_indexed_headers(
        self, rows: typeIterable, column_names: typeList[str]
    ) -> typeNoReturn:
        """default behavior of csvheaders is called without any modifying flags"""
        outs = self.text_csv_writer()
        outs.writerow(("index", "field"))
        for idx, colname in enumerate(column_names, self.column_start_index):
            outs.writerow((idx, colname))

    def _prepare_headers(self) -> typeTuple[typeIterable]:
        """besides returning (rows, column_names,), this sets self.generic_columnized to True/False """

        rows = self.text_csv_reader()
        if not any(
            h
            for h in (
                self.zap_header,
                self.add_header,
            )
        ):
            self.generic_columnized = False
            column_names = next(rows)
        else:
            self.generic_columnized = True
            # Peek at a row to get the number of columns.
            _row = next(rows)
            column_names = [
                f"field_{i}" for i, _c in enumerate(_row, self.column_start_index)
            ]

            if self.args.add_header:
                # then first row (_row) is actually data, not headers to be replaced
                rows = itertools.chain([_row], rows)

        return (
            rows,
            column_names,
        )

    def _set_modes(self, column_names=typeList[str]) -> typeNoReturn:

        self.output_headers_only: bool

        if self.args.rename_headers:
            self.rename_headers = self.parse_rename_param(
                self.args.rename_headers, column_names
            )
        else:
            self.rename_headers = False

        if self.args.regex_headers:
            _pat, _rep = self.args.regex_headers
            self.sed_pattern = re.compile(_pat)
            self.sed_replace = _rep
        else:
            self.sed_pattern = False

        if self.preview:
            self.output_headers_only = True
        elif any(
            m
            for m in (
                self.slugify_mode,
                self.rename_headers,
                self.sed_pattern,
                self.args.add_header,
                self.generic_columnized,
            )
        ):
            self.output_headers_only = False
        else:
            self.output_headers_only = True

    def main(self):
        if self.additional_input_expected():
            self.argparser.error("You must provide an input file or piped data.")

        rows, column_names = self._prepare_headers()

        # set up modes/arguments
        self._set_modes(column_names=column_names)

        if self.rename_headers:
            for rh in self.rename_headers:
                col, rename = rh
                cid = cmk_parse_column_ids(
                    col, column_names, column_offset=self.column_start_index
                )
                if len(cid) != 1:
                    raise ValueError(
                        f"{col} is expected to refer to exactly 1 column name/id, but found: {len(cid)}"
                    )
                else:
                    column_names[cid[0]] = rename

        if self.sed_pattern:
            for i, colname in enumerate(column_names):
                column_names[i] = self.sed_pattern.sub(self.sed_replace, colname)

        if self.slugify_mode:
            for i, colname in enumerate(column_names):
                column_names[i] = cmk_slugify(colname)

        ## time to output
        if self.output_headers_only:
            self.output_indexed_headers(rows, column_names)
        else:
            outs = self.text_csv_writer()
            outs.writerow(column_names)
            outs.writerows(rows)


def launch_new_instance():
    utility = CSVHeader()
    utility.run()


if __name__ == "__main__":
    launch_new_instance()
