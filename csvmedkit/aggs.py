from csvmedkit import agate

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
