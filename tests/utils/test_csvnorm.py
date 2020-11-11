import contextlib

# from subprocess import Popen, PIPE

from io import StringIO
import sys

from tests.mk import (
    CmkTestCase,
    ColumnsTests,
    EmptyFileTests,
    stdin_as_string,
    patch,
    skiptest,
)

from csvmedkit.exceptions import ColumnIdentifierError
from csvmedkit.utils.csvnorm import CSVNorm, Helpers, launch_new_instance


class TestCSVNorm(CmkTestCase):
    Utility = CSVNorm


class TestInit(TestCSVNorm, ColumnsTests, EmptyFileTests):
    default_args = []
    columns_args = []

    def test_launch_new_instance(self):
        with patch.object(
            sys, "argv", [self.Utility.__name__.lower(), "examples/dummy.csv"]
        ):
            launch_new_instance()


class TestBasics(TestCSVNorm):
    def test_dummy(self):
        """
        Shouldn't alter a file with no whitespace/nonprintable characters whatsoever
        """
        self.assertLines(
            ["examples/dummy.csv"],
            [
                "a,b,c",
                "1,2,3",
            ],
        )

    def test_stripping(self):
        """
        leading and trailing whitespace should be removed
        from the data but not the headers
        """

        input_file = StringIO("d, e ,f \n1 ,  2 ,  3 ")
        with stdin_as_string(input_file):
            self.assertLines(
                [],
                [
                    "d, e ,f ",
                    "1,2,3",
                ],
            )

    def test_squeezing(self):
        """
        consecutive whitespace and newlines \n are collapsed
        (and stripping is applied)
        """
        input_file = StringIO('a, b ,c\n11,2   2,"3 \n\n 3"')
        with stdin_as_string(input_file):
            self.assertLines(
                [],
                [
                    "a, b ,c",
                    "11,2 2,3 3",
                ],
            )

    def test_char_norming(self):
        r"""all whitespace converted to either ' ' or '\n', before being processed"""
        # horizontal norm
        self.assertEqual(Helpers.norm_chars("a\tb  c "), "a b  c ")
        # vertical norm
        self.assertEqual(Helpers.norm_chars("a b\nc\r\nd\n\r"), "a b\nc\n\nd\n\n")


class TestMoreSqueeze(TestCSVNorm):
    @property
    def ifile(self):
        return StringIO('a,b,c\n1, 2  2 ,"\n 3  "\n')

    def test_squeeze_then_strip(self):
        with stdin_as_string(self.ifile):
            self.assertLines(
                [],
                [
                    "a,b,c",
                    "1,2 2,3",
                ],
            )


class TestOptions(TestCSVNorm):
    def test_keep_lines(self):
        r"""--keep-lines prevents squeeze's default conversion of \n to ' '"""
        input_file = StringIO('a, b ,c\n11,2   2,"3 \n\n 3"')
        with stdin_as_string(input_file):
            self.assertLines(
                [
                    "--keep-lines",
                ],
                [
                    "a, b ,c",
                    '11,2 2,"3 ',
                    ' 3"',
                ],
            )

    def test_slugify(self):
        input_file = StringIO('id, Hello ,World\nBond,Good-bye!,"E A R T H\n   Ling!"')
        with stdin_as_string(input_file):
            self.assertLines(
                [
                    "--slugify",
                ],
                [
                    "id, Hello ,World",
                    "bond,good_bye,e_a_r_t_h_ling",
                ],
            )

        # verify alias works
        with stdin_as_string(StringIO("a,b,c\nD-D, E?E, !F! \n")):
            self.assertLines(
                [
                    "-S",
                ],
                [
                    "a,b,c",
                    "d_d,e_e,f",
                ],
            )

    def test_lowercase(self):
        input_file = StringIO("A,B,C\nHello,World !,Good-Bye\n")
        with stdin_as_string(input_file):
            self.assertLines(
                [
                    "--lowercase",
                ],
                ["A,B,C", "hello,world !,good-bye"],
            )

        with stdin_as_string(StringIO("A,B,C\nD,E,F\n")):
            self.assertLines(
                [
                    "-L",
                ],
                [
                    "A,B,C",
                    "d,e,f",
                ],
            )

    def test_uppercase(self):
        input_file = StringIO("a,b,c\nHello,World !,Good-Bye\n")
        with stdin_as_string(input_file):
            self.assertLines(
                [
                    "--uppercase",
                ],
                ["a,b,c", "HELLO,WORLD !,GOOD-BYE"],
            )

        with stdin_as_string(StringIO("a,b,c\nd,e,f\n")):
            self.assertLines(
                [
                    "-U",
                ],
                [
                    "a,b,c",
                    "D,E,F",
                ],
            )


class TestSelectiveColumns(TestCSVNorm):
    @property
    def ifile(self):
        return StringIO('a,b,c,d\nhello, World ,"and \n\n  Good?", bye  ! \n')

    def test_selective_norming(self):
        with stdin_as_string(self.ifile):
            self.assertLines(
                [
                    "-c",
                    "2-3",
                ],
                [
                    "a,b,c,d",
                    "hello,World,and Good?, bye  ! ",
                ],
            )

    def test_selective_slugifying(self):
        with stdin_as_string(self.ifile):
            self.assertLines(
                [
                    "--columns",
                    "b,c",
                    "-S",
                ],
                [
                    "a,b,c,d",
                    "hello,world,and_good, bye  ! ",
                ],
            )


class TestEdgeCases(TestCSVNorm):
    @property
    def ifile(self):
        return StringIO("A,B,C\nHello,Wor?ld !,Good-Bye\n")

    def test_slugify_overrides_lower_and_upper(self):
        """
        makes no sense for user to specify both slugify and upper/lower. But if they do, we silently handle it,
        as slugify's effects overrides lower/upper
        """
        with stdin_as_string(self.ifile):
            self.assertLines(
                [
                    "-U",
                    "-S",
                ],
                [
                    "A,B,C",
                    "hello,wor_ld,good_bye",
                ],
            )

        with stdin_as_string(self.ifile):
            self.assertLines(
                [
                    "-L",
                    "-S",
                ],
                [
                    "A,B,C",
                    "hello,wor_ld,good_bye",
                ],
            )


class TestErrors(TestCSVNorm):
    def test_upper_and_lower_cannot_both_be_set(self):
        ioerr = StringIO()
        with contextlib.redirect_stderr(ioerr):
            with self.assertRaises(SystemExit) as e:
                u = self.get_output(["-L", "-U", "examples/dummy.csv"])

        self.assertEqual(e.exception.code, 2)
        self.assertIn(r"Cannot set both --lower and --upper options", ioerr.getvalue())


###################################################################################################
### Tests that verify my documentation examples
###################################################################################################
class TestDocExamples(TestCSVNorm):
    """Tests that verify my documentation examples"""

    pass

    # @property
    # def ifile(self):
    #     return StringIO("")

    # def test_intro_example(self):
    #     pass
