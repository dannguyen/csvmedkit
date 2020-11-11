from csvmedkit import agate
from csvmedkit.cmk.helpers import *
from csvmedkit.exceptions import InvalidAggregateName
from typing import (
    List as ListType,
    NoReturn as NoReturnType,
    Tuple as TupleType,
    Optional as OptionalType,
)


# from csvmedkit.agate.aggregations import (
#     Count,
#     Min,
#     Max,
#     MaxLength,
#     Mean,
#     Median,
#     Mode,
#     StDev,
#     Sum,
# )

Aggregates = {
    "count": agate.aggregations.Count,
    "max": agate.aggregations.Max,
    "maxlength": agate.aggregations.MaxLength,
    "min": agate.aggregations.Min,
    "mean": agate.aggregations.Mean,
    "median": agate.aggregations.Median,
    "mode": agate.aggregations.Mode,
    "stdev": agate.aggregations.StDev,
    "sum": agate.aggregations.Sum,
}


class Aggy(object):
    """
    a happy agate-aware data-unaware object, blissfully oblivious about the dataset it will be applied to
    e.g. it doesn't know or care whether `args` refers to a column name, nevermind whether it is a valid column name for a
        given dataset
    """

    def __init__(self, slug: str, args: list, output_name: OptionalType[str]):
        self._slug = slug
        self._args = args
        self._output_name = output_name

        self._aggregate = self.get_agg(self.slug)

    @property
    def aggregate_class(self) -> type:
        return self._aggregate

    @property
    def aggregation(self) -> agate.Aggregation:
        return self.aggregate_class(*self._args)

    @property
    def agg_args(self) -> ListType[str]:
        d = self._args.copy()
        return d

    @property
    def column_name(self) -> OptionalType[str]:
        """basically, agg_args[0]"""
        return self._args[0] if self._args else None

    @property
    def title(self) -> str:
        if self._output_name:
            """specific name was specified"""
            _name = self._output_name
        else:
            """derive from aggregate function and given arguments"""
            _name = [self.slug, "of", *self._args]
            _name = cmk_slugify(_name)

        return _name

    @property
    def slug(self) -> str:
        return self._slug.lower()

    @staticmethod
    def get_agg(slug: str) -> type:
        try:
            agg = Aggregates[slug]
        except KeyError as err:
            raise InvalidAggregateName(
                f"""Invalid aggregation: "{slug}". Call command with option '--list-aggs' to get a list of available aggregations"""
            )
        else:
            return agg

    @classmethod
    def parse_aggy_string(klass, argtext: str):
        """
        argtext is something like:

        - 'count'
        - 'sum(age)'
        - 'mean|The Average'
        - 'count:state,NY|New Yorker count'
        """
        rtext: str = argtext
        # extract agg_slug
        rtext, output_name = cmk_parse_delimited_str(rtext, delimiter="|", minlength=2)
        # extract agg_args
        agg_slug, agg_args = cmk_parse_delimited_str(rtext, delimiter=":", minlength=2)
        # parse any individual agg_args
        agg_args = cmk_parse_delimited_str(agg_args)

        return klass(agg_slug, agg_args, output_name)
