# import contextlib
# from io import StringIO
# from subprocess import Popen, PIPE
import sys

from unittest import skip as skiptest, TestCase
from unittest.mock import patch

from csvmedkit.exceptions import InvalidAggregation
from csvmedkit.moreutils.csvpivot import CSVPivot, launch_new_instance
from csvmedkit.moreutils.csvpivot import Aggregates, parse_aggregate_string_arg

from tests.tk import CSVKitTestCase, EmptyFileTests, stdin_as_string


class TestCSVPivot(CSVKitTestCase):
    Utility = CSVPivot
    default_args = ["-r", "a"]


class TestInit(TestCSVPivot, EmptyFileTests):
    def test_launch_new_instance(self):
        with patch.object(
            sys,
            "argv",
            [self.Utility.__name__.lower(), "-r", "a", "examples/dummy.csv"],
        ):
            launch_new_instance()

    def test_print_list_of_aggs(self):
        expected_output = ["List of aggregate functions:"] + [
            f"- {a}" for a in Aggregates.keys()
        ]
        self.assertLines(["--list-aggs"], list(expected_output))
        self.assertLines(["-L"], list(expected_output))
        self.assertLines(["-a", ""], list(expected_output))


class TestDefaultCount(TestCSVPivot):
    """
    if -a/--agg isn't specified, it is 'count' by default
    """

    def test_count_rows(self):
        self.assertRows(
            ["-r", "code", "examples/statecodes.csv"],
            [
                ["code", "count_of"],
                ["IA", "1"],
                ["RI", "1"],
                ["TN", "1"],
            ],
        )

    def test_count_column(self):
        """just -c/--pivot-column"""
        self.assertRows(
            ["-c", "code", "examples/statecodes.csv"],
            [["IA", "RI", "TN"], ["1", "1", "1"]],
        )

    def test_count_rows_and_cols(self):
        self.assertRows(
            [
                "--pivot-column",
                "code",
                "--pivot-rows",
                "name",
                "examples/statecodes.csv",
            ],
            [
                ["name", "IA", "RI", "TN"],
                ["Iowa", "1", "0", "0"],
                ["Rhode Island", "0", "1", "0"],
                ["Tennessee", "0", "0", "1"],
            ],
        )

    ################################
    # test
    def test_count_multi_rows(self):
        """
        -r accepts multiple column names
        """
        self.assertRows(
            ["-r", "gender,race", "examples/peeps.csv"],
            [
                ["gender", "race", "count_of"],
                ["female", "white", "1"],
                ["female", "black", "2"],
                ["female", "asian", "1"],
                ["male", "asian", "1"],
                ["male", "latino", "1"],
            ],
        )

    def test_count_multi_rows_and_col(self):
        self.assertLines(
            ["-r", "gender,race", "-c", "name", "examples/peeps.csv"],
            [
                "gender,race,Joe,Jill,Julia,Joan,Jane,Jim",
                "female,white,1,0,0,0,0,0",
                "female,black,0,1,1,0,0,0",
                "female,asian,0,0,0,1,0,0",
                "male,asian,0,0,0,0,1,0",
                "male,latino,0,0,0,0,0,1",
            ],
        )


class TestAggCount(TestCSVPivot):
    """
    test the --a/--agg argument and options, and just the Count aggregation, which is a special
        case since it handles up to 2 optional args
    """

    def test_explicit_agg_count(self):
        """count is the default aggregate method, but we can also explicitly specify it"""
        self.assertRows(
            ["--agg", "count", "-r", "gender", "examples/peeps.csv"],
            [
                ["gender", "count_of"],
                ["female", "4"],
                ["male", "2"],
            ],
        )

    def test_rename_agg_count(self):
        self.assertRows(
            [
                "-a",
                "count|The Count of Monte Cristo!",
                "-r",
                "gender",
                "examples/peeps.csv",
            ],
            [
                ["gender", "The Count of Monte Cristo!"],
                ["female", "4"],
                ["male", "2"],
            ],
        )

    def test_agg_count_non_nulls(self):
        self.assertRows(
            ["-r", "name", "-a", "count:items", "examples/naitems.csv"],
            [
                ["name", "count_of_items"],
                ["Alice", "2"],
                ["Bob", "2"],
                ["Chaz", "0"],
            ],
        )

    def test_agg_count_with_1_arg(self):
        self.assertRows(
            ["-a", "count:age", "-r", "gender", "examples/peeps.csv"],
            [
                ["gender", "count_of_age"],
                ["female", "4"],
                ["male", "2"],
            ],
        )

        self.assertRows(
            ["-a", "count:age|Age Count", "-r", "gender", "examples/peeps.csv"],
            [
                ["gender", "Age Count"],
                ["female", "4"],
                ["male", "2"],
            ],
        )

    def test_agg_count_with_2_args_plain_text(self):
        self.assertRows(
            ["-a", "count:race,asian", "-r", "gender", "examples/peeps.csv"],
            [
                ["gender", "count_of_race_asian"],
                ["female", "1"],
                ["male", "1"],
            ],
        )

        # expected 0 counts
        self.assertRows(
            ["-a", "count:race,a", "-r", "gender", "examples/peeps.csv"],
            [
                ["gender", "count_of_race_a"],
                ["female", "0"],
                ["male", "0"],
            ],
        )

        # with custom name columns
        self.assertRows(
            ["-a", "count:race,black|The Count", "-r", "gender", "examples/peeps.csv"],
            [
                ["gender", "The Count"],
                ["female", "2"],
                ["male", "0"],
            ],
        )

    @skiptest(
        "Need to implement typecasting of second argument to count, especially when number"
    )
    def test_agg_count_with_2_args_typecast(self):
        self.assertRows(
            ["-a", "count:age,25", "-r", "gender", "examples/peeps.csv"],
            [
                ["gender", "count_of_age_25"],
                ["female", "2"],
                ["male", "1"],
            ],
        )


class TestAggs(TestCSVPivot):
    """basic sanity check on all available aggs"""

    def test_agg_sum(self):
        self.assertRows(
            ["-r", "gender", "-a", "sum:age", "examples/peeps.csv"],
            [
                ["gender", "sum_of_age"],
                ["female", "90"],
                ["male", "45"],
            ],
        )

    def test_agg_max(self):
        self.assertRows(
            ["-r", "race", "-a", "max:age", "examples/peeps2.csv"],
            [
                ["race", "max_of_age"],
                ["white", "40"],
                ["asian", "60"],
                ["black", "40"],
                ["latino", "50"],
            ],
        )

    def test_agg_mean(self):
        self.assertRows(
            ["-r", "gender", "-a", "mean:age", "examples/peeps2.csv"],
            [
                ["gender", "mean_of_age"],
                ["female", "42.5"],
                ["male", "40"],
            ],
        )

    def test_agg_median(self):
        self.assertRows(
            ["-r", "gender", "-a", "median:age", "examples/peeps2.csv"],
            [
                ["gender", "median_of_age"],
                ["female", "40"],
                ["male", "40"],
            ],
        )

    def test_agg_mode(self):
        self.assertRows(
            ["-r", "gender", "-a", "mode:age", "examples/peeps2.csv"],
            [
                ["gender", "mode_of_age"],
                ["female", "40"],
                ["male", "30"],
            ],
        )

    def test_agg_min(self):
        self.assertRows(
            ["-r", "race", "-a", "min:age", "examples/peeps2.csv"],
            [
                ["race", "min_of_age"],
                ["white", "40"],
                ["asian", "30"],
                ["black", "30"],
                ["latino", "50"],
            ],
        )

    def test_agg_max_length(self):
        self.assertRows(
            ["-r", "race", "-a", "maxlength:name", "examples/peeps2.csv"],
            [
                ["race", "maxlength_of_name"],
                ["white", "5"],
                ["asian", "5"],
                ["black", "11"],
                ["latino", "6"],
            ],
        )

    def test_agg_stdev(self):
        self.assertRows(
            ["-r", "gender", "-a", "stdev:age", "examples/peeps2.csv"],
            [
                ["gender", "stdev_of_age"],
                ["female", "12.58305739211791616206114134"],
                ["male", "14.14213562373095048801688724"],
            ],
        )


##################################
# error situations
###################################
class TestErrors(TestCSVPivot):
    def test_invalid_aggregation_specified(self):
        with self.assertRaises(InvalidAggregation) as e:
            u = self.get_output(["-c", "b", "-a", "just magic!", "examples/dummy.csv"])
        self.assertIn(
            'Invalid aggregation: "just magic!". Call `-L/--list-aggs` to get a list of available aggregations',
            str(e.exception),
        )


##################################
# parse_aggregate_string_arg
##################################
class TestAggParser(TestCase):
    def test_agg_name(self):
        """just the aggregate name, no arguments or column names to check against"""
        ag = parse_aggregate_string_arg("count")
        self.assertEqual(Aggregates["count"], ag.agg)
        self.assertEqual("count_of", ag.name)
        self.assertEqual([], ag.agg_args)

    def test_agg_name_rename(self):
        ag = parse_aggregate_string_arg("count|Hello")
        self.assertEqual(Aggregates["count"], ag.agg)
        self.assertEqual("Hello", ag.name)
        self.assertEqual([], ag.agg_args)

        ag = parse_aggregate_string_arg('count|"Hello,goodday|and bye"')
        self.assertEqual(Aggregates["count"], ag.agg)
        self.assertEqual("Hello,goodday|and bye", ag.name)

    def test_agg_and_args(self):
        colnames = [
            "a",
            "b",
            "Hello,world",
            "c",
        ]
        ag = parse_aggregate_string_arg("sum:c", valid_columns=colnames)
        self.assertEqual(Aggregates["sum"], ag.agg)
        self.assertEqual("sum_of_c", ag.name)
        self.assertEqual(
            [
                "c",
            ],
            ag.agg_args,
        )

        ag = parse_aggregate_string_arg('count:b,"Hello,world"', colnames)
        self.assertEqual(Aggregates["count"], ag.agg)
        self.assertEqual("count_of_b_hello_world", ag.name)
        self.assertEqual(
            [
                "b",
                "Hello,world",
            ],
            ag.agg_args,
        )

    def test_full_monty(self):
        colnames = [
            "a",
            "b",
            "Hello,world",
            "c",
        ]
        ag = parse_aggregate_string_arg("sum:c|Sum of C", valid_columns=colnames)
        self.assertEqual(Aggregates["sum"], ag.agg)
        self.assertEqual(
            [
                "c",
            ],
            ag.agg_args,
        )
        self.assertEqual("Sum of C", ag.name)

        ag = parse_aggregate_string_arg(
            'count:a,"Hello,world"|"Counts, are |Fun|"', valid_columns=colnames
        )
        self.assertEqual(Aggregates["count"], ag.agg)
        self.assertEqual(
            [
                "a",
                "Hello,world",
            ],
            ag.agg_args,
        )
        self.assertEqual("Counts, are |Fun|", ag.name)


#############################
# Examples
#############################
class TestExamples(TestCSVPivot):
    def test_examples_count_rows(self):
        self.assertRows(
            ["-r", "race", "examples/peeps.csv"],
            [
                ["race", "count_of"],
                ["white", "1"],
                ["asian", "2"],
                ["black", "2"],
                ["latino", "1"],
            ],
        )

    def test_examples_count_multi_rows(self):
        self.assertLines(
            ["-r", "race,gender", "examples/peeps.csv"],
            [
                "race,gender,count_of",
                "white,female,1",
                "asian,male,1",
                "asian,female,1",
                "black,female,2",
                "latino,male,1",
            ],
        )

    def test_examples_count_cols(self):
        self.assertRows(
            ["-c", "gender", "examples/peeps.csv"],
            [
                ["female", "male"],
                ["4", "2"],
            ],
        )

    def test_examples_count_rows_n_cols(self):
        self.assertRows(
            ["-r", "race", "-c", "gender", "examples/peeps.csv"],
            [
                [
                    "race",
                    "female",
                    "male",
                ],
                [
                    "white",
                    "1",
                    "0",
                ],
                [
                    "asian",
                    "1",
                    "1",
                ],
                [
                    "black",
                    "2",
                    "0",
                ],
                [
                    "latino",
                    "0",
                    "1",
                ],
            ],
        )
