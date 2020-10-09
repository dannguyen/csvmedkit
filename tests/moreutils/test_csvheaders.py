from io import StringIO
from unittest.mock import patch
from unittest import skip as skiptest
import sys

from csvmedkit.exceptions import *
from csvmedkit.moreutils.csvheaders import (
    CSVHeaders,
    launch_new_instance,
)

from tests.tk import CSVKitTestCase, EmptyFileTests, stdin_as_string


class TestCSVHeaders(CSVKitTestCase, EmptyFileTests):
    Utility = CSVHeaders

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

    def test_add_generic_headers(self):
        self.assertLines(
            ["--add-headers", "examples/dummy.csv"],
            [
                "field_1,field_2,field_3",
                "a,b,c",
                "1,2,3",
            ],
        )

        self.assertLines(
            ["--HA", "--zero", "examples/dummy.csv"],
            [
                "field_0,field_1,field_2",
                "a,b,c",
                "1,2,3",
            ],
        )

    def test_add_craploads_of_generic_headers(self):
        txt = ",".join(str(i) for i in range(100))
        infile = StringIO(f"{txt}\n")
        with stdin_as_string(infile):
            self.assertLines(
                ["--add-headers"],
                [",".join(f"field_{i}" for i in range(1, 101)), txt],
            )
        infile.close()

    def test_zap_headers(self):
        self.assertLines(
            ["--zap-headers", "examples/dummy.csv"],
            [
                "field_1,field_2,field_3",
                "1,2,3",
            ],
        )

        self.assertLines(
            ["--HZ", "--zero", "examples/dummy.csv"],
            [
                "field_0,field_1,field_2",
                "1,2,3",
            ],
        )

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

    def test_sed(self):
        self.assertLines(
            ["-X", r"(\w)", r"_\1_", "examples/dummy.csv"], ["_a_,_b_,_c_", "1,2,3"]
        )

    def test_slugify_mode(self):
        self.assertLines(
            ["--slugify", "examples/heady.csv"],
            [
                "a,b_sharps,sea_shells",
                "100,cats,Iowa",
                "200,dogs,Ohio",
            ],
        )

    def test_preview_mode(self):
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

        # when adding headers
        self.assertLines(
            ["-P", "--HA", "examples/dummy.csv"],
            [
                "index,field",
                "1,field_1",
                "2,field_2",
                "3,field_3",
            ],
        )

        # when slugged
        self.assertLines(
            ["-P", "-S", "examples/heady.csv"],
            [
                "index,field",
                "1,a",
                "2,b_sharps",
                "3,sea_shells",
            ],
        )

        # when rename
        self.assertLines(
            ["-P", "-R", '"b|Bee,  B! "', "examples/dummy.csv"],
            [
                "index,field",
                "1,a",
                '2,"Bee,  B! "',
                "3,c",
            ],
        )

        # when sed
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

    def test_make_headers_no_added_effect_to_add_headers(self):
        self.assertLines(
            ["--HZ", "--HA", "examples/dummy.csv"],
            [
                "field_1,field_2,field_3",
                "a,b,c",
                "1,2,3",
            ],
        )

    def test_make_headers_precedence_over_rename(self):
        self.assertLines(
            ["--HZ", "--rename", "field_1|x,field_2|y,field_3|z", "examples/dummy.csv"],
            ["x,y,z", "1,2,3"],
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

    ###################################################################################################
    ### Tests that verify my examples
    ###################################################################################################
    @skiptest("write out examples later")
    def test_example(self):
        pass
