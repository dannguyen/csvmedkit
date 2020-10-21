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

from csvmedkit.exceptions import *
from csvmedkit.moreutils.csvslice import CSVSlice, launch_new_instance


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
            ["--intervals", "0", "examples/dummy.csv"],
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


class TestRangesIndexes(TestCSVSlice):
    """
    basically, ranges with closed intervals, e.g. '0-12,55-999', as opposed to '-12,55-'
    """

    def test_single_index(self):
        with stdin_as_string(self.ifile):
            self.assertLines(
                ["-i", "0"],
                ["id", "0"],
            )

        with stdin_as_string(self.ifile):
            self.assertLines(
                ["--intervals", "9"],
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


class TestRangesClosedIntervals(TestCSVSlice):
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

    # cancelling these, since argparser does not like hyphen-leading arguments
    # def test_upper_bounded(self):
    #     with stdin_as_string(self.ifile):
    #         self.assertLines(
    #         ['-i', '-4'],
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
    #              ['-i', '-3,2-3,9,0'],
    #             [
    #                 'id',
    #                 '0',
    #                 '1',
    #                 '2',
    #                 '3',
    #                 '9',
    #             ],
    #         )


class TestEdgeCases(TestCSVSlice):
    pass


class TestErrors(TestCSVSlice):
    def test_ranges_is_required(self):
        ioerr = StringIO()
        with contextlib.redirect_stderr(ioerr):
            with self.assertRaises(SystemExit) as e:
                u = self.get_output(["examples/dummy.csv"])
        self.assertEqual(e.exception.code, 2)
        self.assertIn(
            r"the following arguments are required: -i/--intervals", ioerr.getvalue()
        )

    def test_invalid_interval_strings(self):
        with self.assertRaises(IncorrectlyFormattedString) as e:
            u = self.get_output(["-i", "1,a", "examples/dummy.csv"])
        self.assertIn(
            r"Your --intervals argument, '1,a', has an incorrectly formatted value: 'a'",
            str(e.exception),
        )

        with self.assertRaises(IncorrectlyFormattedString) as e:
            u = self.get_output(["-i", "20--20", "examples/dummy.csv"])
        self.assertIn(
            r"Your --intervals argument, '20--20', has an incorrectly formatted value: '20--20'",
            str(e.exception),
        )

        with self.assertRaises(IncorrectlyFormattedString) as e:
            u = self.get_output(["-i", "-5", "examples/dummy.csv"])
        self.assertIn(
            r"Your --intervals argument, '-5', has an incorrectly formatted value: '-5'",
            str(e.exception),
        )

        with self.assertRaises(IncorrectlyFormattedString) as e:
            u = self.get_output(["-i", "1,-5", "examples/dummy.csv"])
        self.assertIn(
            r"Your --intervals argument, '1,-5', has an incorrectly formatted value: '-5'",
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
class TestDocExamples(TestCSVSlice):
    """Tests that verify my documentation examples"""

    pass

    # @property
    # def ifile(self):
    #     return StringIO("")

    # def test_intro_example(self):
    #     pass
