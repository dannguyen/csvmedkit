******
csvsed
******

:command:`csvsed` is a command to do find-and-replace on a per-column basis.


For example, given a ``data.csv`` like this:

.. code-block:: text

    id,name
    1,Mrs. Adams
    2,Miss Miller
    3,Mrs Smith


Replace by patternTKTK::


    $ csvsed '(Mrs|Miss|Ms)\.?' 'Ms.' data.csv
    id,name
    1,Ms. Adams
    2,Ms. Miller
    3,Ms. Smith


.. contents:: Table of contents
   :local:
   :depth: 3



Usage reference
===============


-c, --columns <columns_list>
----------------------------

A comma separated list of column indices, names or ranges to be affected, e.g. "1,id,3-5". Defaults to all columns.

-m, --match-literal
-------------------

By default, [PATTERN] is assumed to be a regular expression. Set this flag to do a literal match and replacement.


-F, --filter
------------

Only return rows that matched [PATTERN]. This has the same effect as operating on data filtered and piped from ``csvgrep -r (or -m) [PATTERN]``

The main reason to use this is for terseness.

Given ``data.csv`` like this::

    id,name,val
    1,2,3x
    3,4,5
    6,7y,8z


And TK:

.. code-block:: text

    $ csvsed -F '[a-z]' '%' data.csv
    id,name,val
    1,2,3%
    6,7%,8%




.. code-block:: sh

    $ csvsed -F -c 1-20  'pattern' 'replace' data.csv


Versus TKTK::


    $ csvgrep --any-match -c 1-20 -r pattern data.csv | csvsed -c 1-20 'pattern' 'replace'





High level description
======================

Like ``sed``, but on a per-column basis


Example::

    $ csvsed "Ab[bi].+" "Abby" -E "(B|R)ob.*" "\1ob" -E "(?:Jack|John).*" "John"  examples/aliases.csv


    id,to,from
    1,Abby,Bob
    2,Bob,John
    3,Abby,John
    4,John,Abner
    5,Rob,John
    6,Jon,Abby
    7,Rob,Abby


Real-world use cases
====================


.. include:: /scenarios/babynames-csvsed-yearclean.rstinc
