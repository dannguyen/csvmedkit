import contextlib
from io import StringIO
import sys

from csvmedkit import agate
from csvmedkit.cmk.aggs import Aggy, Aggregates


from tests.mk import (
    TestCase,
    skiptest,
)


class TestParseAggyString(TestCase):
    def test_basic(self):
        ag = Aggy.parse_aggy_string("count")
        assert isinstance(ag, Aggy)
        self.assertEqual(ag.slug, "count")
        self.assertEqual(ag.title, "count_of")
        self.assertEqual(ag.agg_args, [])
        assert isinstance(ag.aggregation, agate.Aggregation)

    def test_custom_title(self):
        ag = Aggy.parse_aggy_string("count|Hello")
        self.assertEqual(ag.title, "Hello")
        self.assertEqual(ag.agg_args, [])
        self.assertEqual(ag.slug, "count")

        ag = Aggy.parse_aggy_string('count|"Hello,goodday|and bye"')
        self.assertEqual(
            ag.title,
            "Hello,goodday|and bye",
        )
        self.assertEqual(ag.slug, "count")

    def test_with_single_arg(self):
        ag = Aggy.parse_aggy_string("sum:c")
        self.assertEqual(ag.agg_args, ["c"])
        self.assertEqual(ag.slug, "sum")
        self.assertEqual(ag.title, "sum_of_c")

    def test_with_multiple_args(self):
        ag = Aggy.parse_aggy_string(r'count:hello,"foo, Bar!t"')
        self.assertEqual(ag.agg_args, ["hello", "foo, Bar!t"])
        self.assertEqual(ag.slug, "count")
        self.assertEqual(ag.title, "count_of_hello_foo_bar_t")

    def test_full_monty(self):
        txt = "sum:c|Sum of Fun"
        ag = Aggy.parse_aggy_string(txt)
        self.assertEqual(ag.slug, "sum")
        self.assertEqual(ag.title, "Sum of Fun")
        self.assertEqual(ag.agg_args, ["c"])

        txt = 'count:a,"Hello,world"|"Counts, are |Fun|"'
        ag = Aggy.parse_aggy_string(txt)
        self.assertEqual(ag.slug, "count")
        self.assertEqual(ag.title, "Counts, are |Fun|")
        self.assertEqual(ag.agg_args, ["a", "Hello,world"])


class TestEdgeAggy(TestCase):
    @skiptest(
        "Need to revisit how cmkutil.cmk_parse_delimited_str handles escaped chars"
    )
    def test_pipes_everywhere(self):
        txt = 'count:hello,"foo|bar"|"Actual Title|really"'
        ag = Aggy.parse_aggy_string(txt)
        self.assertEqual(ag.slug, "count")
        self.assertEqual(ag.agg_args, ["hello", "foo|bar"])
        self.assertEqual(ag.title, "Actual Title|really")
