*********
csvheader
*********



:command:`csvheader` is a command for listing and changing the headers of CSV-formatted data.


For example, given a ``data.csv`` containing this

.. code-block:: text

    Case #,X,Y,I.D.
    1,2,3,4
    5,6,7,8


You can *slugify* the headers::

    $ csvheader -S data.csv
    case,x,y,i_d
    1,2,3,4
    5,6,7,8

And/or selectively rename them::

    $ csvheader -R '1|Case Num,4|ID,X|lat,Y|lng' data.csv
    Case Num,lat,lng,ID
    1,2,3,4
    5,6,7,8


.. contents:: Table of contents
   :local:
   :depth: 3


.. include:: csvheader-reference.rstinc

.. include:: csvheader-overview.rstinc

.. include:: csvheader-comparison.rstinc






Real-world use cases TK
=======================


.. include:: /scenarios/babynames-csvheader.rstinc
