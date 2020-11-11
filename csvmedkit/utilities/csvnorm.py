# import csv
# from io import StringIO
# import itertools
from typing import (
    List as ListType,
    Iterable as IterableType,
    NoReturn as NoReturnType,
    Optional as OptionalType,
    Tuple as TupleType,
)

from csvmedkit import agate, re_plus as re
from csvmedkit.cmk.cmkutil import CmkUtil, UniformReader
from csvmedkit.cmk.helpers import cmk_parse_column_ids, cmk_slugify


class Helpers:
    @classmethod
    def norm_chars(klass, txt: str) -> str:
        r"""
        Converts:
            - all horizontal non-printable characters to ' '
            - all vertical non-printable characters to '\n'
        """
        newtxt = txt
        newtxt = re.sub(r"\h", " ", newtxt)
        newtxt = re.sub(r"\r|\v|\f", "\n", newtxt)
        return newtxt

    @classmethod
    def squeeze_space(klass, txt: str, keep_lines: bool = False) -> str:
        r"""
        Collapses consecutive whitespace. Assumes all whitespace is either ' ' or '\n'
        """
        newtxt = txt
        if keep_lines:
            newtxt = re.sub(r" +", " ", newtxt)
            newtxt = re.sub(r"\n+", "\n", newtxt)
        else:
            newtxt = re.sub(r"[ \n]+", " ", newtxt)
        return newtxt

    @classmethod
    def normtext(klass, txt: OptionalType[str], **kwargs) -> str:
        newtxt = txt
        if newtxt:
            newtxt = klass.norm_chars(newtxt)
            newtxt = klass.squeeze_space(newtxt, keep_lines=kwargs.get("keep_lines"))
            newtxt = newtxt.strip()
        return newtxt

    @classmethod
    def transformtext(klass, txt: OptionalType[str], **kwargs) -> str:
        newtxt = txt
        if newtxt:
            if kwargs.get("slugify"):
                newtxt = cmk_slugify(newtxt)
            # slugify mode will always override effects of lowercase/uppercase
            # no need to repeat it if user accidentally specifies slugify and upper/lower
            elif kwargs.get("lowercase"):
                newtxt = newtxt.lower()
            elif kwargs.get("uppercase"):
                newtxt = newtxt.upper()
        return newtxt


class CSVNorm(UniformReader, Helpers, CmkUtil):
    description = """Normalize whitespace and non-printable characters"""
    override_flags = [
        "l",
    ]

    @property
    def keep_lines_mode(self) -> bool:
        return True if self.args.keep_lines else False

    @property
    def lowercase_mode(self) -> bool:
        return True if self.args.lowercase else False

    @property
    def uppercase_mode(self) -> bool:
        return True if self.args.uppercase else False

    @property
    def slugify_mode(self) -> bool:
        return True if self.args.slugify else False

    def add_arguments(self):
        self.argparser.add_argument(
            "-c",
            "--columns",
            dest="columns",
            metavar="<COLUMNS>",
            help="""A list of columns to apply csvnorm's effects. <COLUMNS> should be a comma separated list of column indices, names or ranges to be extracted, e.g. "1,id,3-5". Defaults to all columns.""",
        )

        self.argparser.add_argument(
            "-S",
            "--slugify",
            action="store_true",
            help="""Convert values to snake_case style""",
        )
        self.argparser.add_argument(
            "-L",
            "--lowercase",
            action="store_true",
            help="""Transform letters into lowercase""",
        )
        self.argparser.add_argument(
            "-U",
            "--uppercase",
            action="store_true",
            help="""Transform letters into uppercase""",
        )

        self.argparser.add_argument(
            "--keep-lines",
            action="store_true",
            help="""Do not convert newline characters to regular whitespace""",
        )

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

        if self.lowercase_mode and self.uppercase_mode:
            self.argparser.error("Cannot set both --lower and --upper options")

        working_col_ids = cmk_parse_column_ids(
            self.args.columns,
            self.i_column_names,
            column_offset=self.column_start_index,
        )

        writer = agate.csv.writer(self.output_file, **self.writer_kwargs)
        writer.writerow(self.i_column_names)

        for row in self.i_rows:
            for j, cval in enumerate(row):
                if j in working_col_ids:
                    xval = self.normtext(cval, keep_lines=self.keep_lines_mode)
                    xval = self.transformtext(
                        xval,
                        lowercase=self.lowercase_mode,
                        uppercase=self.uppercase_mode,
                        slugify=self.slugify_mode,
                    )
                    row[j] = xval
            writer.writerow(row)


def launch_new_instance():
    utility = CSVNorm()
    utility.run()


if __name__ == "__main__":
    launch_new_instance()
