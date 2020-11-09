********
csvslice
********

:command:`csvslice` is a command for selecting rows by 0-based index and/or inclusive ranges.


For example, given ``data.csv`` that contains::

    id,val
    a,0
    b,1
    c,2
    d,3


.. code-block:: shell

    $ csvslice -i 0,2-3 data.csv
    id,val
    a,0
    c,2
    d,3




.. contents:: Table of contents
   :local:
   :depth: 3




Options and flags
=================

``csvslice`` has only one unique and required option: ``-i/--intervals``


-i, --intervals <intervals>
---------------------------

`<intervals>` is a comma-delimited list of interval values representing indexes or ranges to be sliced from the 0-indexed dataset.

An interval can take these forms::

- ``-i 0`` — returns the very first row
- ``-i 3-5`` - returns rows in the inclusive index range of 3 to 5
- ``-i '5-'`` — returns all rows with index 5 or more


Multiple interval values can be passed into ``-i/--intervals``, e.g.

.. code-block:: sh

    csvslice -i '0-5,12,15-18,42-' data.csv




.. note:: This is a required option.




Usage overview and examples
===========================


These examples refer to data as found in :download:`ids.csv </../examples/ids.csv>`


Slicing individual rows by index
--------------------------------

You can specify rows to be sliced by 0-based index:


.. code-block:: sh

    csvslice -i 1 ids.csv
    id,val
    1,b



You can also specify a series of individual indexes as a comma-delimited string:


.. code-block:: sh

    csvslice -i 0,5 ids.csv
    id,val
    0,a
    5,f




Slicing rows by range
---------------------

Rows can be specified by using a range syntax: ``start-end``

The range is *inclusive*:


.. code-block:: sh

    $ csvslice -i 1-3 ids.csv
    id,val
    1,b
    2,c
    3,d


Omitting the right-side *end* value returns an open range of values:

.. code-block:: sh

    $ csvslice -i 3- ids.csv
    id,val
    3,d
    4,e
    5,f



Like indexes, a series of ranges can be specified as a comma-delimited string:


.. code-block:: sh

    $ csvslice -i 0-1,3- ids.csv
    id,val
    0,a
    1,b
    3,d
    4,e
    5,f



And you can combine ranges with individual indexes:

.. code-block:: sh

    $ csvslice -i 0,2-3,5 ids.csv
    id,val
    0,a
    2,c
    3,d
    5,f



Errors and quirks
-----------------


Even though ``3-1`` and is technically a valid range, ``csvslice`` will throw an error if the ``end`` value is smaller than the ``start`` value::

.. code-block:: sh

    $ csvslice -i 3-1 examples/ids.csv
    InvalidRange: Invalid range specified: 3-1


For the most part, though, ``csvslice`` will allow the user to pass in a messy or otherwise nonsensical value for ``-i/--intervals``.

No matter what order you specify the indexes and ranges, it will always return rows in sequential order::

.. code-block:: sh

    $ csvslice -i 4,0,2 ids.csv
    id,val
    0,a
    2,c
    4,e


.. code-block:: sh

    $ csvslice -i 4,0-2,3 ids.csv
    id,val
    0,a
    1,b
    2,c
    3,d
    4,e


If you pass in repeated indexes and/or overlapping ranges, ``csvslice`` will still only return the original, sequential data, i.e. it will *not* return duplicates of rows:

.. code-block:: sh

    $ csvslice -i 3,1,3,1,1 ids.csv
    id,val
    1,b
    3,d


.. code-block:: sh

    $ csvslice -i 1,0-2,1-3 ids.csv
    id,val
    0,a
    1,b
    2,c
    3,d

.. TODOTODO
.. And references to non-existent row indexes are also ignored:


.. .. code-block:: sh

..     csvslice -i 5,42 ids.csv
..     id,val
..     5,f



How csvslice compares to existing tools
=======================================


head/tail
---------

csvkit --skip-lines
-------------------


xsv slice
---------


Getting a single record by index::

    xsv slice -i 12 data.csv

    csvslice -i 12 data.csv



Getting a range of records::

    xsv slice -s 5 -e 12

    csvslice -i 5-12


Getting records from index 14 on::

    xsv slice -s 14


    csvslice -i '14-'


Getting the first 13 records::

    xsv slice -e 13


    csvslice -i '0-12'


Agate
-----

TK


pandas
------










Usecases
========

TK
