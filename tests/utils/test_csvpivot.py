# from io import StringIO
# from subprocess import Popen, PIPE
import contextlib
from io import StringIO
import sys


from csvmedkit.exceptions import (
    ColumnIdentifierError,
    ColumnNameError,
    InvalidAggregationArgument,
    InvalidAggregateName,
)
from csvmedkit.utils.csvpivot import CSVPivot, Parser, launch_new_instance
from csvmedkit.cmk.aggs import Aggy, Aggregates


from tests.mk import (
    agate,
    CmkTestCase,
    EmptyFileTests,
    TestCase,
    stdin_as_string,
    skiptest,
    patch,
)


class TestCSVPivot(CmkTestCase):
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
        # self.assertLines(["-L"], list(expected_output)) # -L is now used for --locale
        # self.assertLines(["-a", ""], list(expected_output))


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


class TestCountTypeCast(TestCSVPivot):
    """
    special edge case when passing 2 args into count, with the first arg pointing to a non-text column,
        but the 2nd arg interpreted from command-line as string by default
    """

    # @skiptest(
    #     "Need to implement typecasting of second argument to count, especially when number"
    # )
    def test_agg_count_with_second_arg_intended_as_age(self):
        self.assertRows(
            ["-a", "count:age,25", "-r", "gender", "examples/peeps.csv"],
            [
                ["gender", "count_of_age_25"],
                ["female", "2"],
                ["male", "1"],
            ],
        )

    def test_agg_count_with_second_arg_intended_as_date(self):
        self.assertLines(
            ["-a", "count:when,1950-01-01", "-r", "where", "examples/pdates.csv"],
            [
                "where,count_of_when_1950_01_01",
                "TX,1",
                "CA,2",
                "NY,0",
            ],
        )
        # works with non iso format too, via agate's typecasting

        # TODO: ...and the derived slugged title should reflect this typecasting
        # - is that desirable? Leaving it as such for now b/c don't want to mangle with Aggy class
        self.assertLines(
            ["-a", 'count:when,"Jan. 1, 1950"', "-r", "where", "examples/pdates.csv"],
            [
                "where,count_of_when_1950_01_01",
                "TX,1",
                "CA,2",
                "NY,0",
            ],
        )

    def test_error_when_typecast_of_count_second_arg_fails(self):
        """
        thrown by csvpivot.validate_thingy
        """
        with self.assertRaises(agate.CastError) as e:
            u = self.get_output(
                ["-r", "a", "--agg", "count:b,Bert", "examples/dummy.csv"]
            )
        self.assertIn(
            "You attempted to count 'Bert' in column 'b', which has datatype Number",
            str(e.exception),
        )


class TestNonCountAggregates(TestCSVPivot):
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


class TestInferenceCompat(TestCSVPivot):
    """make sure csvpivot honors --no-inference disabling"""

    def test_no_inference_obeyed(self):
        """
        normally, trying to count 'WHAT' in age:Number would throw an error, but not
        if it's treated like text
        """
        self.assertRows(
            ["-I", "-a", "count:age,WHAT", "-r", "gender", "examples/peeps.csv"],
            [
                ["gender", "count_of_age_what"],
                ["female", "0"],
                ["male", "0"],
            ],
        )


class TestMultiAgg(TestCSVPivot):
    """
    when --pivot-column is empty, but --agg
    """

    def test_simple_double(self):
        """
        essentially: data.groupby(gender).aggregate(count, sum:age)
        """
        self.assertLines(
            [
                "-r",
                "gender",
                "-a",
                "count",
                "-a",
                "sum:age",
                "examples/peeps.csv",
            ],
            [
                "gender,count_of,sum_of_age",
                "female,4,90",
                "male,2,45",
            ],
        )

    def test_triple(self):
        self.assertLines(
            [
                "-r",
                "gender,race",
                "-a",
                "count",
                "-a",
                "mean:age",
                "-a",
                "sum:age|The-Total-Age",
                "examples/peeps.csv",
            ],
            [
                "gender,race,count_of,mean_of_age,The-Total-Age",
                "female,white,1,20,20",
                "female,black,2,22.5,45",
                "female,asian,1,25,25",
                "male,asian,1,20,20",
                "male,latino,1,25,25",
            ],
        )


##################################
# error situations
###################################
class TestErrors(TestCSVPivot):
    def test_invalid_column_name_for_pivot_row(self):
        with self.assertRaises(ColumnIdentifierError) as e:
            u = self.get_output(["-r", "a, hey", "examples/dummy.csv"])
        self.assertIn(
            "Column ' hey' is invalid.",
            str(e.exception),
        )

    def test_invalid_column_name_for_pivot_column(self):
        with self.assertRaises(ColumnIdentifierError) as e:
            u = self.get_output(["-c", "heycol", "examples/dummy.csv"])
        self.assertIn(
            "Column 'heycol' is invalid.",
            str(e.exception),
        )

    def test_invalid_aggregation_method_specified(self):
        with self.assertRaises(InvalidAggregateName) as e:
            u = self.get_output(["-c", "b", "-a", "just magic!", "examples/dummy.csv"])
        self.assertIn(
            """Invalid aggregation: "just magic!". Call command with option '--list-aggs' to get a list of available aggregations""",
            str(e.exception),
        )

    def test_invalid_column_name_given_to_aggregation(self):
        with self.assertRaises(ColumnNameError) as e:
            u = self.get_output(
                ["-r", "gender", "-a", "count:height", "examples/peeps.csv"]
            )
        self.assertIn(
            """'height' is not a valid column name; column names are: ['name', 'race', 'gender', 'age']""",
            str(e.exception),
        )

    def test_invalid_column_name_given_to_aggregation_first_of_2_args(self):
        """
        b/c csvpivot.validate_thingy() has special handling for this count-2-args edge case,
            it does its own lookup of a column name in the loaded self.intable, and
            for now we emit a special error message
        """
        with self.assertRaises(ColumnNameError) as e:
            u = self.get_output(
                ["-r", "a", "--agg", "count:XXX,YYY", "examples/dummy.csv"]
            )
        self.assertIn(
            """'XXX' is not a valid column name; column names are: ['a', 'b', 'c']""",
            str(e.exception),
        )

    def test_more_than_one_pivot_col_specified(self):
        ioerr = StringIO()
        with contextlib.redirect_stderr(ioerr):
            with self.assertRaises(SystemExit) as err:
                u = self.get_output(["-c", "1,3", "examples/dummy.csv"])

        self.assertEqual(err.exception.code, 2)
        self.assertIn("Only one -c/--pivot-column is allowed, not 2", ioerr.getvalue())


###################################################################################################
### Tests that verify my documentation examples
###################################################################################################
class TestDocExamples(TestCSVPivot):
    """Tests that verify my documentation examples"""

    @skiptest("write out examples later")
    def test_intro(self):
        pass

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
