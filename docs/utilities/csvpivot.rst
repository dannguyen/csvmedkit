********
csvpivot
********

:command:`csvpivot` is a command for producing simple pivot tables.

TK TK TK  Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod


.. contents:: Table of contents
   :local:
   :depth: 3




Usage reference
===============

``--list-aggs``
---------------

List the available aggregate functions.

The available aggregate functions are a subset of those implemented in `Agate's Aggregations API <https://agate.readthedocs.io/en/latest/api/aggregations.html>`_

- count
- max
- maxlength
- min
- mean
- median
- mode
- stdev
- sum


``-r, --pivot-rows PIVOT_ROWNAMES``
-----------------------------------

The column name(s) on which to use as pivot rows.
Should be either one name (or index) or a comma-
separated list with one name (or index)


``-c, --pivot-column PIVOT_COLNAME``
------------------------------------

Optionally, a column name/id to use as a pivot
column. Only one is allowed


``-a, --agg AGGREGATES_LIST``
-----------------------------

The name of an aggregation to perform on each group
of data in the pivot table. For aggregations that
require an argument (i.e. a column name), pass in
the aggregation name, followed by a colon, followed
by comma-delimited arguments, e.g. `-a "sum:age"`
and `-a "count:name,hello" To see a list, run
`csvpivot --list-aggs`


High level overview
===================

Pivot Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
proident, sunt in culpa qui officia deserunt mollit anim id est laborum.


Example of TK (what's the word for this) rows given a single column name, and counting the frequency of values::


    $ csvpivot -r 'race' examples/peeps.csv
    race,count_of
    white,1
    asian,2
    black,2
    latino,1



Example of pivoting (TK whats the word) given multiple rows and a column, and counting the combinations::


    $ csvpivot -r 'race' -c 'gender' examples/peeps.csv
    race,female,male
    white,1,0
    asian,1,1
    black,2,0
    latino,0,1






How it compares to existing tools
=================================


Excel/Google Sheets
-------------------

TK

pandas.pivot_table()
--------------------

https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.pivot_table.html

agate.Table.pivot()
-------------------

https://agate.readthedocs.io/en/1.6.1/api/table.html#agate.Table.pivot

https://agate.readthedocs.io/en/1.6.1/cookbook/transform.html?highlight=pivot#pivot-by-a-single-column

https://agate.readthedocs.io/en/1.6.1/cookbook/transform.html?highlight=pivot#pivot-by-multiple-columns

https://agate.readthedocs.io/en/1.6.1/cookbook/transform.html?highlight=pivot#pivot-to-sum

(can't do this) https://agate.readthedocs.io/en/1.6.1/cookbook/transform.html?highlight=pivot#pivot-to-percent-of-total




Usecases
========


Counting Congress demographics::

    $ csvpivot -r party -c gender  examples/congress.csv  | csvlook

    | party       |   M |   F |
    | ----------- | --- | --- |
    | Democrat    | 174 | 107 |
    | Independent |   2 |   0 |
    | Republican  | 229 |  24 |
    | Libertarian |   1 |   0 |


Federal judges

https://www.pewresearch.org/fact-tank/2020/07/15/how-trump-compares-with-other-recent-presidents-in-appointing-federal-judges/


.. code-block:: text

    $ csvpivot examples/real/fed-judges-service.csv -r 'Appointing President' -c 'ABA Rating' \
        | csvheader -R '1|President' \
        | csvcut -c 1,3,2,5,6 \
        | csvlook

    | President          | Well Qualified | Qualified | None | Not Qualified |
    | ------------------ | -------------- | --------- | ---- | ------------- |
    | Barack Obama       |            206 |       124 |    0 |             0 |
    | Ronald Reagan      |            175 |       182 |   25 |             0 |
    | Jimmy Carter       |            130 |       110 |   18 |             3 |
    | Gerald Ford        |             27 |        37 |    3 |             0 |
    | William J. Clinton |            237 |       143 |    0 |             3 |
    | George W. Bush     |            230 |        93 |    0 |             4 |
    | Richard M. Nixon   |             87 |       105 |   17 |             0 |
    | Donald J. Trump    |            158 |        56 |    0 |             7 |
    | George H.W. Bush   |            113 |        80 |    1 |             0 |

Limitations/future fixes
========================

If there are any NULL or irregular values in a column that is being summed/max/min/most aggregations, agate.Table will throw an error.

See more info about that issue here: https://github.com/wireservice/agate/issues/714#issuecomment-681176978

Assuming that agate's behavior can't/won't be changed, a possible solution is filling a to-be-aggregated column with non-null values (i.e. ``0``). However, we should give the user the option of specifying that value. Also, it should probably require explicit enabling, so users who aren't aware their data contains non-null/numeric values are noisily informed.



