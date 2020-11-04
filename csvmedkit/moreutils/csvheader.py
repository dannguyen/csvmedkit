import csv
from io import StringIO
import itertools
from typing import (
    List as typeList,
    Iterable as typeIterable,
    NoReturn as typeNoReturn,
    Optional as typeOptional,
    Tuple as typeTuple,
)

from csvmedkit import re_plus as re
from csvmedkit.cmk.cmkutil import CmkUtil
from csvmedkit.cmk.helpers import (
    cmk_parse_column_ids,
    cmk_parse_delimited_str,
    cmk_slugify,
)


class CSVHeader(CmkUtil):
    description = """Prints flattened records, such that each row represents a record's fieldname and corresponding value,
                     similar to transposing a record in spreadsheet format"""

    override_flags = [
        "l",
        "H",
    ]

    def add_arguments(self):
        self.argparser.add_argument(
            "-A",
            "--add",
            dest="add_header",
            action="store_true",
            help="""Add a header row of generic, numbered column names, starting from 1, e.g. field_1, field_2, and so on.""",
        )

        self.argparser.add_argument(
            "-B",
            "--bash",
            dest="bash_header",
            action="store_true",
            help="""Bash (i.e. completely replace) the current header row with generic column names, e.g. field_1, field_2.""",
        )

        self.argparser.add_argument(
            "-C",
            "--create",
            dest="create_header",
            metavar="<column_names>",
            type=str,
            help="""Similar to `--add`, but specify column names with a comma-delimited string, e.g. 'ID,cost,"name, proper"'""",
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
    def bash_header(self) -> bool:
        return self.args.bash_header

    @property
    def create_header(self) -> typeOptional[list]:
        if self.args.create_header:
            return cmk_parse_delimited_str(
                self.args.create_header, delimiter=","
            )  # TK: do proper delimitation
        else:
            return None

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

        if self.add_header or self.bash_header or self.create_header:
            # sample first row to get a count of columns
            c_row = next(rows)
            if self.create_header:
                column_names = self.create_header
                if len(column_names) != len(c_row):
                    raise ValueError(
                        f"The data has {len(c_row)} columns, but {len(column_names)} column names were parsed from: `{self.args.create_header}`"
                    )
            else:
                # then it's generic column names
                column_names = [
                    f"field_{i}" for i, _c in enumerate(c_row, self.column_start_index)
                ]

            # add_header and create_header assume the data had no header
            # which means c_row is actually data and needs to be added back in
            if self.add_header or self.create_header:
                rows = itertools.chain([c_row], rows)

        # all other options assume the data is "normal",
        # i.e. the first row is the header row
        else:
            column_names = next(rows)

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
                self.add_header,
                self.bash_header,
                self.create_header,
                self.rename_headers,
                self.slugify_mode,
                self.sed_pattern,
                # self.generic_columnized,  # i.e. a add_header or bash_header
                # self.args.create_header,
            )
        ):
            self.output_headers_only = False
        else:
            self.output_headers_only = True

    def main(self):
        if self.additional_input_expected():
            self.argparser.error("You must provide an input file or piped data.")

        if 1 < sum(
            1 if i else 0
            for i in (self.add_header, self.bash_header, self.create_header)
        ):
            self.argparser.error(
                "The --add, --bash, and --create options are mutually exclusive; pick one and only one"
            )

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
