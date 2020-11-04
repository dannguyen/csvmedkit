import contextlib
from io import StringIO
from unittest import skip as skiptest
import sys

from csvmedkit.moreutils.csvheader import (
    CSVHeader,
    launch_new_instance,
)

from tests.mk import CmkTestCase, EmptyFileTests, stdin_as_string, patch, skiptest
from csvmedkit.exceptions import *


class TestCSVHeader(CmkTestCase):
    Utility = CSVHeader


class TestInit(TestCSVHeader, EmptyFileTests):
    def test_launch_new_instance(self):
        with patch.object(
            sys, "argv", [self.Utility.__name__.lower(), "examples/dummy.csv"]
        ):
            launch_new_instance()

    def test_basic(self):
        """default behavior is to print list of headers in index,field format"""
        self.assertLines(
            ["examples/dummy.csv"],
            [
                "index,field",
                "1,a",
                "2,b",
                "3,c",
            ],
        )

    def test_zero_index(self):
        self.assertLines(
            ["--zero", "examples/dummy.csv"],
            [
                "index,field",
                "0,a",
                "1,b",
                "2,c",
            ],
        )


class TestAddHeader(TestCSVHeader):
    def test_add_basic(self):
        self.assertLines(
            ["--add", "examples/dummy.csv"],
            [
                "field_1,field_2,field_3",
                "a,b,c",
                "1,2,3",
            ],
        )

    def test_add_w_zero(self):
        self.assertLines(
            ["-A", "--zero", "examples/dummy.csv"],
            [
                "field_0,field_1,field_2",
                "a,b,c",
                "1,2,3",
            ],
        )

    def test_add_craploads_of_headers(self):
        txt = ",".join(str(i) for i in range(100))
        infile = StringIO(f"{txt}\n")
        with stdin_as_string(infile):
            self.assertLines(
                ["--add"],
                [",".join(f"field_{i}" for i in range(1, 101)), txt],
            )
        infile.close()


class TestBashHeader(TestCSVHeader):
    def test_bash_basic(self):
        self.assertLines(
            ["--bash", "examples/dummy.csv"],
            [
                "field_1,field_2,field_3",
                "1,2,3",
            ],
        )

    def test_bash_basic_with_zero_col(self):
        self.assertLines(
            ["-B", "--zero", "examples/dummy.csv"],
            [
                "field_0,field_1,field_2",
                "1,2,3",
            ],
        )


class TestCreateHeader(TestCSVHeader):
    def test_create_basic(self):
        self.assertLines(
            ["--create", "x,y,z", "examples/dummy.csv"],
            [
                "x,y,z",
                "a,b,c",
                "1,2,3",
            ],
        )

    def test_create_messy_header(self):
        self.assertLines(
            ["--create", 'x,"y,y","z,\nz"', "examples/dummy.csv"],
            [
                'x,"y,y","z,',
                'z"',
                "a,b,c",
                "1,2,3",
            ],
        )

    def test_create_error_too_few_names_given(self):
        with self.assertRaises(ValueError) as e:
            self.get_output(
                ["--create", "x,y", "examples/dummy.csv"],
            )

        self.assertIn(
            """The data has 3 columns, but 2 column names were parsed from: `x,y`""",
            str(e.exception),
        )

    def test_create_error_too_many_names_given(self):
        with self.assertRaises(ValueError) as e:
            self.get_output(
                ["--create", "w,x,y,z", "examples/dummy.csv"],
            )

        self.assertIn(
            """The data has 3 columns, but 4 column names were parsed from: `w,x,y,z`""",
            str(e.exception),
        )


class TestRename(TestCSVHeader):
    def test_rename_mode_basic(self):
        self.assertLines(
            [
                "--rename",
                'a|apples,"b|B-Sharps!","c|Sea, shells "',
                "examples/dummy.csv",
            ],
            ['apples,B-Sharps!,"Sea, shells "', "1,2,3"],
        )

    def test_rename_by_index(self):
        self.assertLines(
            ["-R", 'a|apples,3|cello,"2|Be, Bee"', "examples/dummy.csv"],
            [
                'apples,"Be, Bee",cello',
                "1,2,3",
            ],
        )

    def test_rename_by_zero_index(self):
        self.assertLines(
            ["--zero", "-R", 'a|apples,2|cello,"1|Be, Bee"', "examples/dummy.csv"],
            [
                'apples,"Be, Bee",cello',
                "1,2,3",
            ],
        )

        self.assertLines(
            [
                "--zero",
                "--preview",
                "-R",
                'a|apples,2|cello,"1|Be, Bee"',
                "examples/dummy.csv",
            ],
            [
                "index,field",
                "0,apples",
                '1,"Be, Bee"',
                "2,cello",
            ],
        )

    def test_rename_error_when_bad_column_name(self):
        with self.assertRaises(ColumnIdentifierError) as e:
            self.get_output(["-R", "B|Beta", "examples/dummy.csv"])
        self.assertIn(
            "Column 'B' is invalid. It is neither an integer nor a column name",
            str(e.exception),
        )

    def test_rename_error_when_bad_index(self):
        with self.assertRaises(ColumnIdentifierError) as e:
            self.get_output(["-R", "4|Beta", "examples/dummy.csv"])
        self.assertIn(
            "Column 4 is invalid. The last column is 'c' at index 3", str(e.exception)
        )

    def test_rename_handle_repeated_index(self):
        """
        user shouldn't do this, but no reason why it can't be handled
        """
        # a is changed to 'x'; second op has no effect

        with self.assertRaises(ColumnIdentifierError) as e:
            self.get_output(
                ["-R", "a|x,a|y", "examples/dummy.csv"],
            )
        self.assertIn(
            "Column 'a' is invalid. It is neither an integer nor a column name. Column names are: 'x', 'b', 'c'",
            str(e.exception),
        )

        # a is changed to 'b'; second op affects first 'a'
        self.assertLines(
            ["-R", "a|b,b|z", "examples/dummy.csv"],
            [
                "z,b,c",
                "1,2,3",
            ],
        )

    def test_rename_handle_dupe_headers(self):
        """kind of an edge case"""
        # only first 'a' column is renamed
        self.assertLines(
            ["-R", "a|x", "examples/dupehead.csv"],
            [
                "x,b,a",
                "1,2,3",
            ],
        )

        # though successive dupes will get at it
        self.assertLines(
            ["-R", "a|x,a|y", "examples/dupehead.csv"],
            [
                "x,b,y",
                "1,2,3",
            ],
        )

    @skiptest("TODO")
    def test_rename_when_names_have_pipe_edge_case(self):
        """edge case"""
        pass


class TestSlugify(TestCSVHeader):
    def test_slugify_mode(self):
        self.assertLines(
            ["--slugify", "examples/heady.csv"],
            [
                "a,b_sharps,sea_shells",
                "100,cats,Iowa",
                "200,dogs,Ohio",
            ],
        )


class TestRegex(TestCSVHeader):
    def test_regex(self):
        self.assertLines(
            ["-X", r"(\w)", r"_\1_", "examples/dummy.csv"], ["_a_,_b_,_c_", "1,2,3"]
        )

        self.assertLines(
            ["--regex", r"(\w)", r"_\1_", "examples/dummy.csv"],
            ["_a_,_b_,_c_", "1,2,3"],
        )


class TestPreviewMode(TestCSVHeader):
    def test_default(self):
        """
        prints only headers, even if --slugify and/or --rename is used
        """
        # no different than basic default behavior
        self.assertLines(
            ["--preview", "examples/dummy.csv"],
            [
                "index,field",
                "1,a",
                "2,b",
                "3,c",
            ],
        )

    def test_add_headers(self):
        # when adding headers
        self.assertLines(
            ["-P", "-A", "examples/dummy.csv"],
            [
                "index,field",
                "1,field_1",
                "2,field_2",
                "3,field_3",
            ],
        )

    def test_rename(self):
        """prettify after renaming"""
        self.assertLines(
            ["-P", "-R", '"b|Bee,  B! "', "examples/dummy.csv"],
            [
                "index,field",
                "1,a",
                '2,"Bee,  B! "',
                "3,c",
            ],
        )

    def test_slugify(self):
        """prettify after slugify"""
        self.assertLines(
            ["-P", "-S", "examples/heady.csv"],
            [
                "index,field",
                "1,a",
                "2,b_sharps",
                "3,sea_shells",
            ],
        )

    def test_regexing(self):
        """prettify after regexing"""
        self.assertLines(
            ["-P", "-X", "(a|c)", r"Foo, \1", "examples/dummy.csv"],
            [
                "index,field",
                '1,"Foo, a"',
                "2,b",
                '3,"Foo, c"',
            ],
        )


######################################
### order of operations
######################################
class TestOrderOps(TestCSVHeader):
    """
    making sure the order of operations of transformations is what we expect
    """

    def test_rename_precedence_over_add(self):
        """kind of an edge case..."""
        self.assertLines(
            ["-A", "--rename", "field_1|x,field_2|y,field_3|z", "examples/dummy.csv"],
            ["x,y,z", "a,b,c", "1,2,3"],
        )

    def test_rename_precedence_over_bash(self):
        """kind of an edge case..."""
        self.assertLines(
            ["-B", "-R", "field_1|x,field_2|y,field_3|z", "examples/dummy.csv"],
            ["x,y,z", "1,2,3"],
        )

    def test_rename_precedence_over_create(self):
        """kind of an edge case..."""
        self.assertLines(
            ["-C", "i,j,k", "-R", "i|x,j|y,k|z", "examples/dummy.csv"],
            ["x,y,z", "a,b,c", "1,2,3"],
        )

    def test_rename_then_slug(self):
        """renaming always happens first, then the slugging"""
        self.assertLines(
            [
                "-S",
                "--rename",
                'a|Alice,"b|big-bob!","c| CA. "',
                "examples/dummy.csv",
            ],
            ["alice,big_bob,ca", "1,2,3"],
        )

    def test_rename_then_sed(self):
        """renaming always happens first, then the slugging"""
        self.assertLines(
            [
                "-X",
                "(a|b)",
                r"!\1!",
                "-R",
                'a|apples,"b|B-Sharps!","c|Sea, shells "',
                "examples/dummy.csv",
            ],
            ['!a!pples,B-Sh!a!rps!,"Se!a!, shells "', "1,2,3"],
        )

    def test_sed_then_slug(self):
        """renaming always happens first, then the slugging"""
        self.assertLines(
            ["-S", "-X", "(c|b)", r" F O \1 O ", "examples/dummy.csv"],
            ["a,f_o_b_o,f_o_c_o", "1,2,3"],
        )


class TestHelpStringExamples(TestCSVHeader):
    def test_rename_helpdoc(self):
        self.assertLines(
            [
                "-R",
                "a|Apples,2|hello,3|world",
                "examples/dummy.csv",
            ],
            ["Apples,hello,world", "1,2,3"],
        )

    def test_slugify_helpdoc(self):

        ifile = StringIO('APPLES,"Date - Time "\n')
        with stdin_as_string(ifile):
            self.assertLines(
                [
                    "-S",
                ],
                [
                    "apples,date_time",
                ],
            )


###################################################################################################
### Tests for errors
###################################################################################################
class TestErrorStuff(TestCSVHeader):
    @property
    def errmsg(self):
        return "The --add, --bash, and --create options are mutually exclusive; pick one and only one"

    def test_add_bash_create_are_exclusive(self):
        ioerr = StringIO()
        with contextlib.redirect_stderr(ioerr):
            with self.assertRaises(SystemExit) as e:
                u = self.get_output(["-A", "-B", "examples/dummy.csv"])
        self.assertEqual(e.exception.code, 2)
        self.assertIn(self.errmsg, ioerr.getvalue())

        # other combinations
        with contextlib.redirect_stderr(StringIO()):
            with self.assertRaises(SystemExit) as e:
                u = self.get_output(["-A", "-C", "x,y,z", "examples/dummy.csv"])
        self.assertEqual(e.exception.code, 2)

        with contextlib.redirect_stderr(StringIO()):
            with self.assertRaises(SystemExit) as e:
                u = self.get_output(["-B", "-C", "x,y,z", "examples/dummy.csv"])
        self.assertEqual(e.exception.code, 2)

        with contextlib.redirect_stderr(StringIO()):
            with self.assertRaises(SystemExit) as e:
                u = self.get_output(["-A", "-B", "-C", "x,y,z", "examples/dummy.csv"])
        self.assertEqual(e.exception.code, 2)


###################################################################################################
### Tests that verify my documentation examples
###################################################################################################
class TestHelpDoc(TestCSVHeader):
    @property
    def idata(self):
        return StringIO("Case #,X,Y,I.D.\n1,2,3,4\n5,6,7,8\n")

    def test_create_helpdoc_midcomma_name(self):
        self.assertLines(
            ["-C", 'ID,cost,"Name, proper"', "examples/dummy.csv"],
            [
                'ID,cost,"Name, proper"',
                "a,b,c",
                "1,2,3",
            ],
        )

    def test_slugify_intro_example(self):
        with stdin_as_string(self.idata):
            self.assertLines(
                ["-S"],
                [
                    "case,x,y,i_d",
                    "1,2,3,4",
                    "5,6,7,8",
                ],
            )

    def test_rename_intro_example(self):
        with stdin_as_string(self.idata):
            self.assertLines(
                ["-R", "1|Case Num,4|ID,X|lat,Y|lng"],
                [
                    "Case Num,lat,lng,ID",
                    "1,2,3,4",
                    "5,6,7,8",
                ],
            )


class TestDocExamplesBabyNames(TestCSVHeader):
    @property
    def idata(self):
        return StringIO("Mary,F,7065\nAnna,F,2604\nEmma,F,2003\n")

    def test_babynames_create_header(self):
        with stdin_as_string(self.idata):
            self.assertLines(
                ["-C", "name,sex,count"],
                [
                    "name,sex,count",
                    "Mary,F,7065",
                    "Anna,F,2604",
                    "Emma,F,2003",
                ],
            )
