import contextlib
from io import StringIO
import sys

from tests.mk import (
    CmkTestCase,
    EmptyFileTests,
    stdin_as_string,
    patch,
    skiptest,
)

from csvmedkit.moreutils.csvslice import CSVSlice, launch_new_instance


class TestCSVSlice(CmkTestCase):
    Utility = CSVSlice

    @property
    def ifile(self):
        return StringIO("id\n" + "\n".join(str(i) for i in range(0, 10)))


class TestInit(TestCSVSlice, EmptyFileTests):
    default_args = []

    def test_launch_new_instance(self):
        with patch.object(
            sys, "argv", [self.Utility.__name__.lower(), "examples/dummy.csv"]
        ):
            launch_new_instance()


class TestRangesIndexes(TestCSVSlice):
    """
    basically, ranges with closed intervals, e.g. '0-12,55-999', as opposed to '-12,55-'
    """

    def test_single_index(self):
        with stdin_as_string(self.ifile):
            self.assertLines(
                ["-r", "0"],
                ["id", "0"],
            )

        with stdin_as_string(self.ifile):
            self.assertLines(
                ["--ranges", "9"],
                ["id", "9"],
            )

    def test_several_indexes(self):
        with stdin_as_string(self.ifile):
            self.assertLines(
                ["-r", "2,0,9,2"],
                [
                    "id",
                    "0",
                    "2",
                    "9",
                ],
            )


class TestRangesClosedIntervals(TestCSVSlice):
    def test_single_interval(self):
        with stdin_as_string(self.ifile):
            self.assertLines(
                ["-r", "3-5"],
                [
                    "id",
                    "3",
                    "4",
                    "5",
                ],
            )

        with stdin_as_string(self.ifile):
            self.assertLines(
                ["-r", "8-10000"],
                [
                    "id",
                    "8",
                    "9",
                ],
            )

    def test_multi_intervals(self):
        with stdin_as_string(self.ifile):
            self.assertLines(
                ["-r", "4-7,0-1,6-8"],
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


class TestRangesOpenIntervals(TestCSVSlice):
    def test_lower_bound(self):
        with stdin_as_string(self.ifile):
            self.assertLines(
                ["-r", "7-"],
                [
                    "id",
                    "7",
                    "8",
                    "9",
                ],
            )

        with stdin_as_string(self.ifile):
            self.assertLines(
                ["-r", "0-2,6-8,7-"],
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
                ["-r", "9-,8,9,7-,8-"],
                [
                    "id",
                    "7",
                    "8",
                    "9",
                ],
            )

    # cancelling these, since argparser does not like hyphen-leading arguments
    # def test_upper_bounded(self):
    #     with stdin_as_string(self.ifile):
    #         self.assertLines(
    #         ['-r', '-4'],
    #             [
    #                 'id',
    #                 '0',
    #                 '1',
    #                 '2',
    #                 '3',
    #                 '4',

    #             ],
    #         )

    #     with stdin_as_string(self.ifile):
    #         self.assertLines(
    #              ['-r', '-3,2-3,9,0'],
    #             [
    #                 'id',
    #                 '0',
    #                 '1',
    #                 '2',
    #                 '3',
    #                 '9',
    #             ],
    #         )


class TestBasics(TestCSVSlice):
    def test_dummy(self):
        self.assertLines(
            ["examples/dummy.csv"],
            [
                "a,b,c",
                "1,2,3",
            ],
        )

    def test_0_index(self):
        self.assertLines(
            ["--index", "0", "examples/dummy.csv"],
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


class TestLengthOption(TestCSVSlice):
    @property
    def ifile(self):
        return StringIO("a,b,c\n1,2,3\n4,5,6\n,7,8,9\n10,11,12\n")

    def test_length_starts_from_0(self):
        """with no --index set, --length assumes user wants n records from the start"""
        with stdin_as_string(self.ifile):
            self.assertLines(
                [
                    "--length",
                    "2",
                ],
                [
                    "a,b,c",
                    "1,2,3",
                    "4,5,6",
                ],
            )


class TestEdgeCases(TestCSVSlice):
    pass


class TestErrors(TestCSVSlice):
    @skiptest("not sure if this is needed...")
    def test_either_index_or_length_must_be_set(self):
        pass

    @skiptest("TODO")
    def test_length_is_more_than_zero(self):
        pass

    # def test_upper_and_lower_cannot_both_be_set(self):
    #     ioerr = StringIO()
    #     with contextlib.redirect_stderr(ioerr):
    #         with self.assertRaises(SystemExit) as e:
    #             u = self.get_output(["-TK", "examples/dummy.csv"])

    #     self.assertEqual(e.exception.code, 2)
    #     self.assertIn(r"TKWHATEVER", ioerr.getvalue())


###################################################################################################
### Tests that verify my documentation examples
###################################################################################################
class TestDocExamples(TestCSVSlice):
    """Tests that verify my documentation examples"""

    pass

    # @property
    # def ifile(self):
    #     return StringIO("")

    # def test_intro_example(self):
    #     pass
