**********
csvheaders
**********



:command:`csvheaders` is a command for listing and changing the headers of CSV-formatted data.


.. contents:: :local:


Description
===========

In its most basic invocation, :command:`csvheaders` simply produces a list of column names in CSV format::

    $ csvheaders examples/heady.csv

    index,field
    1,A
    2, B Sharps
    3,"SEA, shells!"

However, enabling any of its renaming options, such as ``--slug``, will reproduce the input data with its headers renamed::

    $ csvheaders --slugify examples/heady.csv

    a,b_sharps,sea_shells
    100,cats,Iowa
    200,dogs,Ohio



How it compares to existing tools
=================================

Compared to ``csvcut --names``
------------------------------

TK Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
proident, sunt in culpa qui officia deserunt mollit anim id est laborum.


::

    $ csvcut --names examples/heady.csv
      1: A
      2:  B Sharps
      3: SEA, shells!

Compared to ``xsv headers``
---------------------------

::

    $ xsv headers examples/heady.csv

    1   A
    2    B Sharps
    3   SEA, shells!


Compared to ``sed``
-------------------

It's possible to use :command:`sed` to `replace the entire first line <https://superuser.com/a/1026686>`_ of input::

    $ sed '1s/.*/alpha,bravo,charlie/' examples/heady.csv

    alpha,bravo,charlie
    100,cats,Iowa
    200,dogs,Ohio

However, this invocation of :command:`sed` will not work on multi-line headers (which is admittedly, an edge-case).

But ``sed`` can't be used to selectively rename headers — it can only do string replacement. For example, to rename *only* the 1st column requires tailoring a specific regex::

    $ sed '1s/^A/alpha/' examples/heady.csv

    alpha, B Sharps ,"SEA, shells!"
    100,cats,Iowa
    200,dogs,Ohio


Renaming only the 1st *and* 3rd columns gets very messy::


    $ sed -e '1s/^A/alpha/' -e '1s/"SEA.*/charlie/' examples/heady.csv

    alpha, B Sharps ,charlie
    100,cats,Iowa
    200,dogs,Ohio


In contrast, ``csvheaders --rename`` allows for renaming columns by (1-based) index::

    $ csvheaders --rename '1|alpha,3|charlie' examples/heady.csv


    alpha, B Sharps ,charlie
    100,cats,Iowa
    200,dogs,Ohio



Common scenarios and use cases
==============================

TK TK


Reference: Options and usage
============================

TK TK
