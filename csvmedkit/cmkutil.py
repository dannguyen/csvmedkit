"""Main module."""
import argparse
from collections import namedtuple
import sys
from typing import List as typeList, NoReturn as typeNoReturn, Iterable as typeIterable
import warnings

from csvkit.grep import FilteringCSVReader


from csvmedkit import CSVKitUtility, agate, parse_column_identifiers
from csvmedkit import __title__, __version__
from csvmedkit import re_std as re


class CmkUtil(CSVKitUtility):
    """
    slightly adjusted version of standard CSVKitUtility
    """

    def log_err(self, txt: str) -> typeNoReturn:
        stderr.write(f"{txt}\n")

    def text_csv_reader(self) -> agate.csv.reader:
        return agate.csv.reader(self.skip_lines(), **self.reader_kwargs)

    def text_csv_writer(self) -> agate.csv.writer:
        return agate.csv.writer(self.output_file, **self.writer_kwargs)

    def _extract_csv_reader_kwargs(self):
        """
        Extracts those from the command-line arguments those would should be passed through to the input CSV reader(s).
        """
        kwargs = {}

        if self.args.tabs:
            kwargs["delimiter"] = "\t"

        elif self.args.delimiter:
            kwargs["delimiter"] = self.args.delimiter

        for arg in (
            "quotechar",
            "quoting",
            "doublequote",
            "escapechar",
            "field_size_limit",
            "skipinitialspace",
        ):
            value = getattr(self.args, arg, None)
            if value is not None:
                kwargs[arg] = value

        # if six.PY2 and self.args.encoding:
        #     kwargs['encoding'] = self.args.encoding

        if getattr(self.args, "no_header_row", None):
            kwargs["header"] = not self.args.no_header_row

        return kwargs

    def get_column_offset(self):
        """a dumb hack I need for some reason? Because sometimes I need to call this when zero_based is not an arg"""
        if getattr(self.args, "zero_based", None):
            if self.args.zero_based:
                return 0
            else:
                return 1
        else:
            return 1

    def _init_common_parser(self):
        """
        Same as csvkit.cli.CSVKitUtil 1.05, except --version is customized
        """
        self.argparser = argparse.ArgumentParser(
            description=self.description, epilog=self.epilog
        )

        # Input
        if "f" not in self.override_flags:
            self.argparser.add_argument(
                metavar="FILE",
                nargs="?",
                dest="input_path",
                help="The CSV file to operate on. If omitted, will accept input as piped data via STDIN.",
            )
        if "d" not in self.override_flags:
            self.argparser.add_argument(
                "-d",
                "--delimiter",
                dest="delimiter",
                help="Delimiting character of the input CSV file.",
            )
        if "t" not in self.override_flags:
            self.argparser.add_argument(
                "-t",
                "--tabs",
                dest="tabs",
                action="store_true",
                help='Specify that the input CSV file is delimited with tabs. Overrides "-d".',
            )
        if "q" not in self.override_flags:
            self.argparser.add_argument(
                "-q",
                "--quotechar",
                dest="quotechar",
                help="Character used to quote strings in the input CSV file.",
            )
        if "u" not in self.override_flags:
            self.argparser.add_argument(
                "-u",
                "--quoting",
                dest="quoting",
                type=int,
                choices=[0, 1, 2, 3],
                help="Quoting style used in the input CSV file. 0 = Quote Minimal, 1 = Quote All, 2 = Quote Non-numeric, 3 = Quote None.",
            )
        if "b" not in self.override_flags:
            self.argparser.add_argument(
                "-b",
                "--no-doublequote",
                dest="doublequote",
                action="store_false",
                help="Whether or not double quotes are doubled in the input CSV file.",
            )
        if "p" not in self.override_flags:
            self.argparser.add_argument(
                "-p",
                "--escapechar",
                dest="escapechar",
                help='Character used to escape the delimiter if --quoting 3 ("Quote None") is specified and to escape the QUOTECHAR if --no-doublequote is specified.',
            )
        if "z" not in self.override_flags:
            self.argparser.add_argument(
                "-z",
                "--maxfieldsize",
                dest="field_size_limit",
                type=int,
                help="Maximum length of a single field in the input CSV file.",
            )
        if "e" not in self.override_flags:
            self.argparser.add_argument(
                "-e",
                "--encoding",
                dest="encoding",
                default="utf-8",
                help="Specify the encoding of the input CSV file.",
            )
        # if 'L' not in self.override_flags:
        #     self.argparser.add_argument('-L', '--locale', dest='locale', default='en_US',
        #                                 help='Specify the locale (en_US) of any formatted numbers.')
        # if 'S' not in self.override_flags:
        #     self.argparser.add_argument('-S', '--skipinitialspace', dest='skipinitialspace', action='store_true',
        #                                 help='Ignore whitespace immediately following the delimiter.')
        # if 'blanks' not in self.override_flags:
        #     self.argparser.add_argument('--blanks', dest='blanks', action='store_true',
        #                                 help='Do not convert "", "na", "n/a", "none", "null", "." to NULL.')
        # if 'date-format' not in self.override_flags:
        #     self.argparser.add_argument('--date-format', dest='date_format',
        #                                 help='Specify a strptime date format string like "%%m/%%d/%%Y".')
        # if 'datetime-format' not in self.override_flags:
        #     self.argparser.add_argument('--datetime-format', dest='datetime_format',
        #                                 help='Specify a strptime datetime format string like "%%m/%%d/%%Y %%I:%%M %%p".')
        if "H" not in self.override_flags:
            self.argparser.add_argument(
                "-H",
                "--no-header-row",
                dest="no_header_row",
                action="store_true",
                help="Specify that the input CSV file has no header row. Will create default headers (a,b,c,...).",
            )
        if "K" not in self.override_flags:
            self.argparser.add_argument(
                "-K",
                "--skip-lines",
                dest="skip_lines",
                type=int,
                default=0,
                help="Specify the number of initial lines to skip before the header row (e.g. comments, copyright notices, empty rows).",
            )
        if "v" not in self.override_flags:
            self.argparser.add_argument(
                "-v",
                "--verbose",
                dest="verbose",
                action="store_true",
                help="Print detailed tracebacks when errors occur.",
            )

        # Output
        if "l" not in self.override_flags:
            self.argparser.add_argument(
                "-l",
                "--linenumbers",
                dest="line_numbers",
                action="store_true",
                help="Insert a column of line numbers at the front of the output. Useful when piping to grep or as a simple primary key.",
            )

        # Input/Output
        if "zero" not in self.override_flags:
            self.argparser.add_argument(
                "--zero",
                dest="zero_based",
                action="store_true",
                help="When interpreting or displaying column numbers, use zero-based numbering instead of the default 1-based numbering.",
            )

        self.argparser.add_argument(
            "-V",
            "--version",
            action="version",
            version=f"{__title__}.%(prog)s ({__version__})",
            help="Display version information and exit.",
        )


class CmkMixedUtil(CmkUtil):
    """
    just like standard CmkUtil, except parses intermixed args because it has required positional args
    """

    def __init__(self, args=None, output_file=None):
        """
        Perform argument processing and other setup for a CSVKitUtility.

        same as standard, except we use parse_intermixed_args
        """
        self._init_common_parser()
        self.add_arguments()
        self.args = self.argparser.parse_intermixed_args(args)

        # Output file is only set during testing.
        if output_file is None:
            self.output_file = sys.stdout
        else:
            self.output_file = output_file

        self.reader_kwargs = self._extract_csv_reader_kwargs()
        self.writer_kwargs = self._extract_csv_writer_kwargs()

        self._install_exception_handler()

        try:
            import signal

            signal.signal(signal.SIGPIPE, signal.SIG_DFL)
        except (ImportError, AttributeError):
            # Do nothing on platforms that don't have signals or don't have SIGPIPE
            pass

    def run(self):
        """
        Unlike standard .run(), this will behave if self.input_file has already been set
        """
        # if 'f' not in self.override_flags:
        if not getattr(self, "input_file", None):
            self.input_file = self._open_input_file(self.args.input_path)

        try:
            with warnings.catch_warnings():
                if getattr(self.args, "no_header_row", None):
                    warnings.filterwarnings(
                        action="ignore",
                        message="Column names not specified",
                        module="agate",
                    )

                self.main()
        finally:
            # if 'f' not in self.override_flags:
            self.input_file.close()


def cmk_parse_column_ids(
    ids: str, column_names: typeList[str], column_offset=1
) -> typeList[int]:
    """just a simplified version of parse_column_identifiers"""
    return parse_column_identifiers(
        ids, column_names, column_offset, excluded_columns=None
    )


def cmk_filter_rows(
    rows: typeIterable,
    pattern_str: str,
    columns_str: str,
    column_names: list,
    default_column_ids: list,
    literal_match: bool,
    column_offset: int,
    inverse: bool,
    any_match: bool,
    # not_columns,
) -> FilteringCSVReader:

    if literal_match:
        pattern = pattern_str
    else:  # literal match
        pattern = re.compile(pattern_str)

    if columns_str:
        expr_col_ids = parse_column_identifiers(
            columns_str,
            column_names,
            column_offset,
        )
    else:
        expr_col_ids = default_column_ids

    epatterns = dict((eid, pattern) for eid in expr_col_ids)

    filtered_rows = FilteringCSVReader(
        rows,
        header=False,
        patterns=epatterns,
        inverse=inverse,
        any_match=any_match,
    )
    return filtered_rows
