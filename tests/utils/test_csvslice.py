import contextlib
from io import StringIO
from pathlib import Path
import sys

from tests.mk import (
    CmkTestCase,
    EmptyFileTests,
    stdin_as_string,
    patch,
    parameterized,
    skiptest,
)

from csvmedkit.exceptions import *
from csvmedkit.utils.csvslice import CSVSlice, launch_new_instance


class TestCSVSlice(CmkTestCase):
    Utility = CSVSlice

    @property
    def ifile(self):
        return StringIO("id\n" + "\n".join(str(i) for i in range(0, 10)))


class TestInit(TestCSVSlice, EmptyFileTests):
    default_args = ["-i", "1"]

    def test_launch_new_instance(self):
        with patch.object(
            sys,
            "argv",
            [self.Utility.__name__.lower(), *self.default_args, "examples/dummy.csv"],
        ):
            launch_new_instance()


class TestBasics(TestCSVSlice):
    def test_dummy(self):
        self.assertLines(
            ["-i", "0-99999", "examples/dummy.csv"],
            [
                "a,b,c",
                "1,2,3",
            ],
        )

    def test_0_index(self):
        self.assertLines(
            ["--indexes", "0", "examples/dummy.csv"],
            [
                "a,b,c",
                "1,2,3",
            ],
        )
        self.assertLines(
            ["-i", "1", "examples/dummy.csv"],
            [
                "a,b,c",
            ],
        )


class TestIndexes(TestCSVSlice):
    def test_single_index(self):
        with stdin_as_string(self.ifile):
            self.assertLines(
                ["-i", "0"],
                ["id", "0"],
            )

        with stdin_as_string(self.ifile):
            self.assertLines(
                ["--indexes", "9"],
                ["id", "9"],
            )

    def test_several_indexes(self):
        with stdin_as_string(self.ifile):
            self.assertLines(
                ["-i", "2,0,9,2"],
                [
                    "id",
                    "0",
                    "2",
                    "9",
                ],
            )


class TestHead(TestCSVSlice):
    @property
    def ifile(self):
        return StringIO("id\n" + "\n".join(str(i) for i in range(0, 5)))

    def test_basic(self):
        with stdin_as_string(self.ifile):
            self.assertLines(
                ["--head", "2"],
                ["id", "0", "1"],
            )

    def test_out_of_bounds(self):
        with stdin_as_string(self.ifile):
            self.assertLines(
                ["--head", "20"],
                ["id", "0", "1", "2", "3", "4"],
            )


class TestTail(TestCSVSlice):
    @property
    def ifile(self):
        return StringIO("id\n" + "\n".join(str(i) for i in range(0, 5)))

    def test_basic(self):
        with stdin_as_string(self.ifile):
            self.assertLines(
                ["--tail", "2"],
                ["id", "3", "4"],
            )

    def test_out_of_bounds(self):
        with stdin_as_string(self.ifile):
            self.assertLines(
                ["--tail", "20"],
                ["id", "0", "1", "2", "3", "4"],
            )


class TestRangesClosedIntervals(TestCSVSlice):
    """
    basically, ranges with closed intervals, e.g. '0-12,55-999', as opposed to '-12,55-'
    """

    def test_single_interval(self):
        with stdin_as_string(self.ifile):
            self.assertLines(
                ["-i", "3-5"],
                [
                    "id",
                    "3",
                    "4",
                    "5",
                ],
            )

        with stdin_as_string(self.ifile):
            self.assertLines(
                ["-i", "8-10000"],
                [
                    "id",
                    "8",
                    "9",
                ],
            )

    def test_multi_intervals(self):
        with stdin_as_string(self.ifile):
            self.assertLines(
                ["-i", "4-7,0-1,6-8"],
                [
                    "id",
                    "0",
                    "1",
                    "4",
                    "5",
                    "6",
                    "7",
                    "8",
                ],
            )

    def test_zero_range(self):
        """0 can be a special case because sometimes I forget how Python treats 0 as falsy/nonetype"""
        with stdin_as_string(self.ifile):
            self.assertLines(
                ["-i", "0-3"],
                [
                    "id",
                    "0",
                    "1",
                    "2",
                    "3",
                ],
            )

    def test_start_equals_end_is_fine(self):
        """why would user do this, who knows, but it's technically fine"""
        with stdin_as_string(self.ifile):
            self.assertLines(
                ["-i", "0-0"],
                [
                    "id",
                    "0",
                ],
            )

        with stdin_as_string(self.ifile):
            self.assertLines(
                ["-i", "3-3"],
                [
                    "id",
                    "3",
                ],
            )


class TestRangesOpenIntervals(TestCSVSlice):
    def test_lower_bound(self):
        with stdin_as_string(self.ifile):
            self.assertLines(
                ["-i", "7-"],
                [
                    "id",
                    "7",
                    "8",
                    "9",
                ],
            )

    def test_lower_bound_zero_all(self):
        with stdin_as_string(self.ifile):
            self.assertLines(
                ["-i", "1-"],
                [
                    "id",
                    "1",
                    "2",
                    "3",
                    "4",
                    "5",
                    "6",
                    "7",
                    "8",
                    "9",
                ],
            )

    def test_lower_bound_combo(self):
        with stdin_as_string(self.ifile):
            self.assertLines(
                ["-i", "0-2,6-8,7-"],
                [
                    "id",
                    "0",
                    "1",
                    "2",
                    "6",
                    "7",
                    "8",
                    "9",
                ],
            )

    def test_edgy_lower_bound(self):
        """
        for now, we don't warn user if there are overlapping/conflicting bounds
        """
        with stdin_as_string(self.ifile):
            self.assertLines(
                ["-i", "9-,8,9,7-,8-"],
                [
                    "id",
                    "7",
                    "8",
                    "9",
                ],
            )


class TestEdgeCases(TestCSVSlice):
    pass


class TestErrors(TestCSVSlice):
    def test_at_least_one_required_opt(self):
        """
        -i/--indexes used to be the only option, and required.
        With --head and --tail, this is no longer the case...
        """
        ioerr = StringIO()
        with contextlib.redirect_stderr(ioerr):
            with self.assertRaises(SystemExit) as e:
                u = self.get_output(["examples/dummy.csv"])
        self.assertEqual(e.exception.code, 2)
        self.assertIn(
            r"At least one of the following options must be included: --indexes, --head, or --tail",
            ioerr.getvalue(),
        )

    @parameterized.expand(
        [
            (
                "--indexes",
                "1",
                "--head",
                "1",
                "--tail",
                "1",
            ),
            (
                "--indexes",
                "1",
                "--head",
                "1",
            ),
            (
                "--indexes",
                "1",
                "--tail",
                "1",
            ),
            (
                "--head",
                "1",
                "--tail",
                "1",
            ),
        ]
    )
    def test_one_and_only_one_required_opt(self, *opts):
        ioerr = StringIO()
        with contextlib.redirect_stderr(ioerr):
            with self.assertRaises(SystemExit) as e:
                self.get_output([*opts, "examples/dummy.csv"])

        self.assertEqual(e.exception.code, 2)
        opttxt = [opts[0], opts[2]] if len(opts) < 6 else [opts[0], opts[2], opts[4]]
        opttxt = ", ".join(opttxt)
        self.assertIn(
            f"""You specified options {opttxt}. But only one of these options""",
            ioerr.getvalue(),
        )

    @parameterized.expand(
        [
            (
                "--head",
                "0",
            ),
            (
                "--head",
                "-5",
            ),
            (
                "--tail",
                "0",
            ),
            (
                "--tail",
                "-3",
            ),
        ]
    )
    def test_head_and_tail_arg_must_be_greater_than_zero(self, *opts):
        ioerr = StringIO()
        with contextlib.redirect_stderr(ioerr):
            with self.assertRaises(SystemExit) as e:
                self.get_output([*opts, "examples/ids.csv"])

        self.assertEqual(e.exception.code, 2)
        self.assertIn(
            f"""{opts[0]} must be greater than 0, not {opts[1]}""", ioerr.getvalue()
        )

    def test_invalid_indexes_strings(self):
        with self.assertRaises(IncorrectlyFormattedString) as e:
            u = self.get_output(["-i", "1,a", "examples/dummy.csv"])
        self.assertIn(
            r"Your --indexes argument, '1,a', has an incorrectly formatted value: 'a'",
            str(e.exception),
        )

        with self.assertRaises(IncorrectlyFormattedString) as e:
            u = self.get_output(["-i", "20--20", "examples/dummy.csv"])
        self.assertIn(
            r"Your --indexes argument, '20--20', has an incorrectly formatted value: '20--20'",
            str(e.exception),
        )

        with self.assertRaises(IncorrectlyFormattedString) as e:
            u = self.get_output(["-i", "-5", "examples/dummy.csv"])
        self.assertIn(
            r"Your --indexes argument, '-5', has an incorrectly formatted value: '-5'",
            str(e.exception),
        )

        with self.assertRaises(IncorrectlyFormattedString) as e:
            u = self.get_output(["-i", "1,-5", "examples/dummy.csv"])
        self.assertIn(
            r"Your --indexes argument, '1,-5', has an incorrectly formatted value: '-5'",
            str(e.exception),
        )

    def test_be_whiny_about_invalid_ranges(self):
        """
        technically, a range of 6-3, i.e. range(6, 3), is valid – but user should be nosily told about the problem
        """
        with self.assertRaises(InvalidRange) as e:
            u = self.get_output(["-i", "6-3", "examples/dummy.csv"])

        self.assertIn(r"Invalid range specified: 6-3", str(e.exception))


###################################################################################################
### Tests that verify my documentation examples
###################################################################################################
class TestDoc(TestCSVSlice):
    """Tests that verify my documentation examples"""

    src_path = "examples/ids.csv"


class TestDocIntro(TestDoc):
    def test_intro(self):
        data = StringIO("id,val\n0,a\n1,b\n2,c\n3,d\n")
        with stdin_as_string(data):
            self.assertLines(
                ["-i", "0,2-3"],
                [
                    "id,val",
                    "0,a",
                    "2,c",
                    "3,d",
                ],
            )


class TestDocIndexes(TestDoc):
    def test_by_index(self):
        self.assertLines(
            ["-i", "1", self.src_path],
            [
                "id,val",
                "1,b",
            ],
        )

    def test_by_indexes(self):
        self.assertLines(
            ["-i", "0,5", self.src_path],
            [
                "id,val",
                "0,a",
                "5,f",
            ],
        )


class TestDocRanges(TestDoc):
    def test_basic(self):
        self.assertLines(
            ["-i", "1-3", self.src_path],
            [
                "id,val",
                "1,b",
                "2,c",
                "3,d",
            ],
        )

    def test_open_end(self):
        self.assertLines(
            ["-i", "3-", self.src_path],
            [
                "id,val",
                "3,d",
                "4,e",
                "5,f",
            ],
        )

    def test_multiple(self):
        self.assertLines(
            ["-i", "0-1,3-", self.src_path],
            [
                "id,val",
                "0,a",
                "1,b",
                "3,d",
                "4,e",
                "5,f",
            ],
        )

    def test_combo_w_indexes(self):
        self.assertLines(
            ["-i", "0,2-3,5", self.src_path],
            [
                "id,val",
                "0,a",
                "2,c",
                "3,d",
                "5,f",
            ],
        )


class TestDocQuirks(TestDoc):
    def test_range_must_make_sense(self):
        with self.assertRaises(InvalidRange) as e:
            u = self.get_output(["-i", "3-1", "examples/ids.csv"])

        self.assertIn(r"Invalid range specified: 3-1", str(e.exception))

    def test_unordered(self):
        self.assertLines(
            ["-i", "4,0,2", self.src_path],
            [
                "id,val",
                "0,a",
                "2,c",
                "4,e",
            ],
        )

        self.assertLines(
            ["-i", "4,0-2,3", self.src_path],
            [
                "id,val",
                "0,a",
                "1,b",
                "2,c",
                "3,d",
                "4,e",
            ],
        )

    def test_duplicates(self):
        self.assertLines(
            ["-i", "3,1,3,1,1", self.src_path],
            [
                "id,val",
                "1,b",
                "3,d",
            ],
        )

        self.assertLines(
            ["-i", "1,0-2,1-3", self.src_path],
            [
                "id,val",
                "0,a",
                "1,b",
                "2,c",
                "3,d",
            ],
        )

    def test_by_index_nonexistent(self):
        self.assertLines(
            ["-i", "5,42", self.src_path],
            [
                "id,val",
                "5,f",
            ],
        )

        self.assertLines(
            ["-i", "42", self.src_path],
            [
                "id,val",
            ],
        )

    def test_(self):
        self.assertLines(
            ["-i", "0-5", self.src_path],
            [
                "id,val",
                "0,a",
                "1,b",
                "2,c",
                "3,d",
                "4,e",
                "5,f",
            ],
        )


class TestDocComparisons(TestDoc):
    datapath = "examples/ids.csv"

    def test_vs_head(self):
        self.assertCmdLines(
            f"head -n 3 {self.datapath}",
            [
                "id,val",
                "0,a",
                "1,b",
            ],
        )

        self.assertCmdLines(
            f"csvslice --head 3 {self.datapath}",
            [
                "id,val",
                "0,a",
                "1,b",
                "2,c",
            ],
        )

    def test_vs_tail(self):
        self.assertCmdLines(
            f"tail -n 2 {self.datapath}",
            [
                "4,e",
                "5,f",
            ],
        )

        self.assertCmdLines(
            f"csvslice --tail 2 {self.datapath}",
            [
                "id,val",
                "4,e",
                "5,f",
            ],
        )

    def test_vs_xsv_single(self):
        answer = [
            "id,val",
            "2,c",
        ]

        self.assertCmdLines(f"xsv slice -i 2 {self.datapath}", list(answer))

        self.assertCmdLines(f"csvslice -i 2 {self.datapath}", list(answer))

    def test_vs_xsv_first_n(self):
        answer = [
            "id,val",
            "0,a",
            "1,b",
            "2,c",
        ]
        self.assertCmdLines(f"xsv slice -l 3 {self.datapath}", list(answer))

        self.assertCmdLines(f"csvslice --head 3 {self.datapath}", list(answer))

    def test_vs_xsv_range(self):
        answer = [
            "id,val",
            "1,b",
            "2,c",
        ]

        self.assertCmdLines(f"xsv slice -s 1 -e 3 {self.datapath}", list(answer))

        self.assertCmdLines(f"csvslice -i 1-2 {self.datapath}", list(answer))

    # def test_vs_xsv_(self):
    #     self.assertCmdLines(
    #         f'xsv slice    {self.datapath}',
    #         [
    #                 "id,val",
    #                 "0,a",
    #                 "1,b",
    #                 "2,c",
    #                 "3,d",
    #                 "4,e",
    #                 "5,f",
    #         ]
    #     )

    #     self.assertCmdLines(
    #         f'csvslice   {self.datapath}',
    #         [
    #                 "id,val",
    #                 "0,a",
    #                 "1,b",
    #                 "2,c",
    #                 "3,d",
    #                 "4,e",
    #                 "5,f",
    #         ]
    #     )


class TestDocScenarios(TestDoc):
    def getpath(self, path: str) -> str:
        return str(Path("examples/real").joinpath(path))

    def test_acs_csvslice_skip_meta(self):
        src_path = self.getpath("acs-pop.csv")
        self.assertCmdLines(
            f"""csvslice -i '1-' {src_path}""",
            [
                "GEO_ID,NAME,B01003_001E,B01003_001M",
                "0200000US1,Northeast Region,55982803,*****",
                "0200000US2,Midwest Region,68329004,*****",
                "0200000US3,South Region,125580448,*****",
                "0200000US4,West Region,78347268,*****",
            ],
        )
