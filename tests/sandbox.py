#!/usr/bin/env python3

import agate
import csv
import pdb
from pathlib import Path
from IPython import embed as iembed
from agate.aggregations import (
    Count,
    Min,
    Max,
    MaxLength,
    Mean,
    Median,
    Mode,
    StDev,
    Sum,
)


DATA_PATHS = {
    "dummy": Path("examples/dummy.csv"),
    "peeps": Path("examples/peeps.csv"),
    "states": Path("examples/statecodes.csv"),
}

DATA = {}
for k, p in DATA_PATHS.items():
    with open(p) as src:
        DATA[k] = list(csv.DictReader(src))


def main():
    print("Why hello there!")

    peeps = agate.Table.from_object(
        DATA["peeps"]
    )  # , column_types=[agate.Text(cast_nulls=False) for k in DATA['stuff'][0].keys()])
    iembed()


if __name__ == "__main__":
    main()
