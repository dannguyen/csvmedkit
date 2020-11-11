"""
A crapton of redundant repetitive i.e. mostly uselesstests to make sure that CmkMixedUtil utilities,
e.g. csvsed, which allow for intermixed arguments and option/flags, just works, including with implicit and explicit stdin
"""


import contextlib
from io import StringIO

# from subprocess import Popen, PIPE
from pathlib import Path

from tests.mk import (
    CmkTestCase,
    stdin_as_string,
    parameterized,
    skiptest,
)

from csvmedkit.utils.csvsed import CSVSed

DEFAULT_PATH = "examples/dummy2.csv"


class MixCase(CmkTestCase):
    Utility = CSVSed
    default_args = (
        "1",
        "A",
    )
    default_opts = (
        "-c",
        "3,2",
        "-F",
    )

    @property
    def indata(self):
        return StringIO(Path(DEFAULT_PATH).read_text())

    @property
    def answer(self):
        return [
            "a,b,c",
            "8,9,A0",
        ]


class TestHello(MixCase):
    def test_plain(self):
        self.assertLines(
            ["-c", "3,2", "-F", "1", "A", "examples/dummy2.csv"],
            self.answer,
        )

    def test_basic(self):
        self.assertLines(
            [*self.default_opts, *self.default_args, DEFAULT_PATH],
            self.answer,
        )


class GroupedParams(MixCase):
    """options, then args; and args, then options"""

    opts = [
        [("-c", "3,2", "-F")],
        [("-F", "-c", "3,2")],
        [("-Fc", "3,2")],
    ]


class TestGroupedParamsInputFile(GroupedParams):
    """when input_file is an actual file path/object"""

    @parameterized.expand(GroupedParams.opts)
    def test_args_then_opts(self, opts):
        args = [*self.default_args, DEFAULT_PATH]

        self.assertLines([*opts, *args], self.answer)

    @parameterized.expand(GroupedParams.opts)
    def test_opts_then_args(self, opts):
        args = [*self.default_args, DEFAULT_PATH]

        self.assertLines([*opts, *args], self.answer)


class TestGroupedParamsImplicitStdin(GroupedParams):
    """when input_file is piped from stdin, implicitly"""

    margs = GroupedParams.default_args

    @parameterized.expand(GroupedParams.opts)
    def test_args_then_opts(self, opts):
        with stdin_as_string(self.indata):
            self.assertLines([*self.margs, *opts], self.answer)

    @parameterized.expand(GroupedParams.opts)
    def test_opts_then_args(self, opts):
        with stdin_as_string(self.indata):
            self.assertLines(
                [
                    *opts,
                    *self.margs,
                ],
                self.answer,
            )


class TestGroupedParamsExplicitStdin(GroupedParams):
    """when input_file is piped from stdin, with stdin explicitly specified as '-' """

    margs = [*GroupedParams.default_args, "-"]

    @parameterized.expand(GroupedParams.opts)
    def test_args_then_opts(self, opts):
        with stdin_as_string(self.indata):
            self.assertLines([*self.margs, *opts], self.answer)

    @parameterized.expand(GroupedParams.opts)
    def test_opts_then_args(self, opts):
        with stdin_as_string(self.indata):
            self.assertLines(
                [
                    *opts,
                    *self.margs,
                ],
                self.answer,
            )


class MixedParams(MixCase):
    """when the options and args are all over the place!!!"""

    mixed_params = [
        [
            "-F",
            "1",
            "A",
            "-c",
            "3,2",
            DEFAULT_PATH,
        ],
        [
            "-c",
            "3,2",
            "1",
            "A",
            DEFAULT_PATH,
            "-F",
        ],
        [
            "1",
            "-c",
            "3,2",
            "A",
            DEFAULT_PATH,
            "-F",
        ],
        [
            "1",
            "-c",
            "3,2",
            "A",
            "-F",
            DEFAULT_PATH,
        ],
        [
            "1",
            "-c",
            "3,2",
            "-F",
            "A",
            DEFAULT_PATH,
        ],
        [
            "1",
            "-F",
            "A",
            DEFAULT_PATH,
            "-c",
            "3,2",
        ],
        [
            "1",
            "A",
            "-c",
            "3,2",
            DEFAULT_PATH,
            "-F",
        ],
        [
            "1",
            "A",
            "-Fc",
            "3,2",
            DEFAULT_PATH,
        ],
    ]

    @parameterized.expand(mixed_params)
    def test_input_file_path(self, *params):
        """when input_file is an actual file path/object"""
        self.assertLines(params, self.answer)

    @parameterized.expand(mixed_params)
    def test_implicit_stdin(self, *params):
        """when input file is stdin piped int"""
        xarms = list(params)  # .copy()
        xarms.remove(DEFAULT_PATH)
        with stdin_as_string(self.indata):
            self.assertLines(xarms, self.answer)

    @parameterized.expand(mixed_params)
    def test_explicit_stdin(self, *params):
        """when input file is stdin piped in and '-' is passed in as argument"""
        xarms = list(params)  # .copy()
        xarms[xarms.index(DEFAULT_PATH)] = "-"
        with stdin_as_string(self.indata):
            self.assertLines(xarms, self.answer)
