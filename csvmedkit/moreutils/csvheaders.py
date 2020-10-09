import csv
from io import StringIO
import itertools
from typing import (
    List as typeList,
    Iterable as typeIterable,
    NoReturn as typeNoReturn,
    Tuple as typeTuple,
)

from csvmedkit.cmkutil import CmkUtil, cmk_parse_column_ids
from csvmedkit import re_plus as re, slugify


class CSVHeaders(CmkUtil):
    description = """Prints flattened records, such that each row represents a record's fieldname and corresponding value,
                     similar to transposing a record in spreadsheet format"""

    override_flags = [
        "l",
        "H",
    ]

    def add_arguments(self):
        self.argparser.add_argument(
            "--HA",
            "--add-headers",
            dest="add_headers",
            action="store_true",
            help="""Add/prepend headers to the given data, in generic 'field_%%d' format, e.g. 'field_1', 'field_2', etc.""",
        )

        self.argparser.add_argument(
            "--HZ",
            "--zap-headers",
            dest="zap_headers",
            action="store_true",
            help="""Similar to `--HA/--add-headers`, but instead of adding a generic header row, completely replace (i.e. "zap") the current headers""",
        )

        self.argparser.add_argument(
            "-R",
            "--rename",
            dest="rename_headers",
            type=str,
            help="""Comma-delimited list of pipe-delimited pairs:  (existing) column names/ids, and their replacement, e.g. 'col_a|new_a,2|new_b,"3|New C Col"'  """,
        )

        self.argparser.add_argument(
            "-S",
            "--slugify",
            dest="slugify_mode",
            action="store_true",
            help="""Convert all the headers into snakecase, e.g. 'Date-Time ' becomes 'date_time' """,
        )

        self.argparser.add_argument(
            "-X",
            "--regex",
            dest="regex_headers",
            nargs=2,
            type=str,
            help="""Apply a regex replacement to each header: '[PATTERN]' '[REPLACEMENT]'""",
        )

        self.argparser.add_argument(
            "-P",
            "--preview",
            action="store_true",
            help="""Output only the list of headers; use this to preview renamed or otherwise transformed headers without processing the entire input data file""",
        )

    @staticmethod
    def parse_rename_param(
        txt: str, column_names: typeList[str], start_index: int = 1
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
        for idx, colname in enumerate(column_names, self.start_index):
            outs.writerow((idx, colname))

    def _prepare_headers(self) -> typeTuple[typeIterable]:
        """besides returning (rows, column_names,), this sets self.generic_columnized to True/False """

        rows = self.text_csv_reader()
        if not any(
            h
            for h in (
                self.args.zap_headers,
                self.args.add_headers,
            )
        ):
            self.generic_columnized = False
            column_names = next(rows)
        else:
            self.generic_columnized = True
            # Peek at a row to get the number of columns.
            _row = next(rows)
            column_names = [f"field_{i}" for i, _c in enumerate(_row, self.start_index)]

            if self.args.add_headers:
                # then first row (_row) is actually data, not headers to be replaced
                rows = itertools.chain([_row], rows)

        return (
            rows,
            column_names,
        )

    def _set_modes(self, column_names=typeList[str]) -> typeNoReturn:
        self.slugify_mode = True if self.args.slugify_mode else False

        if self.args.rename_headers:
            self.rename_headers = self.parse_rename_param(
                self.args.rename_headers, column_names, self.start_index
            )
        else:
            self.rename_headers = False

        if self.args.regex_headers:
            _pat, _rep = self.args.regex_headers
            self.sed_pattern = re.compile(_pat)
            self.sed_replace = _rep
        else:
            self.sed_pattern = False

        if self.args.preview:
            self.output_headers_only = True
        elif any(
            m
            for m in (
                self.slugify_mode,
                self.rename_headers,
                self.sed_pattern,
                self.args.add_headers,
                self.generic_columnized,
            )
        ):
            self.output_headers_only = False
        else:
            self.output_headers_only = True

    def main(self):
        if self.additional_input_expected():
            self.argparser.error("You must provide an input file or piped data.")

        self.start_index = 0 if getattr(self.args, "zero_based", None) else 1
        rows, column_names = self._prepare_headers()

        # set up modes/arguments
        self._set_modes(column_names=column_names)

        if self.rename_headers:
            for rh in self.rename_headers:
                col, rename = rh
                cid = cmk_parse_column_ids(
                    col, column_names, column_offset=self.start_index
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
                column_names[i] = slugify(colname)

        ## time to output
        if self.output_headers_only:
            self.output_indexed_headers(rows, column_names)
        else:
            outs = self.text_csv_writer()
            outs.writerow(column_names)
            outs.writerows(rows)


def launch_new_instance():
    utility = CSVHeaders()
    utility.run()


if __name__ == "__main__":
    launch_new_instance()
