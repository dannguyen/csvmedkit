#!/usr/bin/env python3


import csv
from io import StringIO
import pdb
from IPython import embed as iembed
from pathlib import Path

import agate
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

import pandas as pd


from csvmedkit.cmk.cmkutil import *
from csvmedkit.cmk.helpers import *
from csvmedkit.cmk.aggs import *

DATA_PATHS = {
    "dummy": Path("examples/dummy.csv"),
    "peeps": Path("examples/peeps.csv"),
    "states": Path("examples/statecodes.csv"),
    'pot': Path('examples/real/denver-pot-sales.csv'),
    'whos': Path('examples/whos.csv'),

}

DATA = {}
for k, p in DATA_PATHS.items():
    with open(p) as src:
        DATA[k] = list(csv.DictReader(src))


def main():
    print("Why hello there!")

    # data = agate.Table.from_object(DATA["whos"])
    # , column_types=[agate.Text(cast_nulls=False) for k in DATA['stuff'][0].keys()])
    table = agate.Table.from_csv('examples/whos.csv')
    outtable = table.group_by(key='gender')
    outtable = outtable.aggregate([('sum_of_age', Sum('age')), ('mean_of_age', Mean('age'))])
    # gpot = pot.group_by(key='YEAR')
    # vpot = pot.pivot(key=['YEAR'])

    iembed()




if __name__ == "__main__":
    main()


"""
path = Path('examples/drafts/fed-judges-service.csv')
jt = agate.Table.from_csv(path)


"""



"""
pivot = table.pivot(
    key=['col1', 'col2',]
    pivot=self.pivot_column_name,
    aggregation=self.pivot_aggregation,
)

vpot = pot.pivot(key=['YEAR'])



"""
