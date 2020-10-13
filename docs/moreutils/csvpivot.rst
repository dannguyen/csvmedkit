********
csvpivot
********

:command:`csvpivot` is a command for producing simple pivot tables

.. contents:: :local:



Description
===========

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


Federal judges::

    $ csvpivot examples/drafts/fed-judges-service.csv -r 'Appointing President' -c 'ABA Rating'

    https://www.pewresearch.org/fact-tank/2020/07/15/how-trump-compares-with-other-recent-presidents-in-appointing-federal-judges/

Limitations/future fixes
========================

If there are any NULL or irregular values in a column that is being summed/max/min/most aggregations, agate.Table will throw an error.

See more info about that issue here: https://github.com/wireservice/agate/issues/714#issuecomment-681176978

Assuming that agate's behavior can't/won't be changed, a possible solution is filling a to-be-aggregated column with non-null values (i.e. ``0``). However, we should give the user the option of specifying that value. Also, it should probably require explicit enabling, so users who aren't aware their data contains non-null/numeric values are noisily informed.



