********
csvpivot
********

:command:`csvpivot` is a command for producing simple pivot tables.


.. contents:: Table of contents
   :local:
   :depth: 3


.. include:: quickstart.rstinc


.. include:: options.rstinc


.. include:: usage.rstinc



.. include:: comparison-spreadsheets.rstinc

.. include:: comparison-pandas.rstinc


.. include:: comparison-cli.rstinc


.. include:: real-usecases.rstinc


Limitations/future fixes
========================

If there are any NULL or irregular values in a column that is being summed/max/min/most aggregations, agate.Table will throw an error.

See more info about that issue here: https://github.com/wireservice/agate/issues/714#issuecomment-681176978

Assuming that agate's behavior can't/won't be changed, a possible solution is filling a to-be-aggregated column with non-null values (i.e. ``0``). However, we should give the user the option of specifying that value. Also, it should probably require explicit enabling, so users who aren't aware their data contains non-null/numeric values are noisily informed.



