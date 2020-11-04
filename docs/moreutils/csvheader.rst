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


Usage reference
===============


-A, --add
---------

Add a header row of generic, numbered column names, starting from 1, e.g. field_1, field_2, and so on.


-B, --bash
----------

Bash (i.e. completely replace) the current header row with generic column names, e.g. field_1, field_2.


-C, --create <column_names>
---------------------------

Similar to ``--add``, but specify column names with a comma-delimited string, e.g. ``'ID,cost,"Name, proper"'``


-R, --rename <renamed_header_pairs>
-----------------------------------

Rename individual columns. The required argument is a comma-delimited string of pipe-delimited pairs — column id/name and the new name.

For example, to rename the "a" column to "Apples"; and also, the 2nd and 3rd columns to "hello" and "world", respectively, the quoted argument string would be:

::

    'a|Apples,2|hello,3|world'


-S, --slugify
-------------

Converts the existing column names to snake_case style. For example, ``APPLES`` and  ``'Date - Time '`` are converted, respectively, to ``'apples'`` and ``'date_time'``.


-X, --regex <pattern> <replacement>
-----------------------------------

In the existing column names, replace all occurrences of a regular expression *<pattern>* with *<replacement>*.



-P, --preview
-------------

When no options are invoked, only the existing header is printed as a comma-delimited list. Invoking any of the aforementioned options prints the transformed header *and* the data. In the latter case, use the ``--preview`` flag to see only what the transformed headers look like.



High level overview
===================

In its most basic invocation, :command:`csvheader` simply produces a list of column names in CSV format::

    $ csvheader examples/heady.csv

    index,field
    1,A
    2, B Sharps
    3,"SEA, shells!"

However, enabling any of its renaming options, such as ``--slug``, will reproduce the input data with its headers renamed::

    $ csvheader --slugify examples/heady.csv

    a,b_sharps,sea_shells
    100,cats,Iowa
    200,dogs,Ohio



How csvheader compares to existing tools
========================================






Compared to adding a header row with ``csvformat --no-header-row``
------------------------------------------------------------------


::

    $ echo '1,2,3,4' | csvformat --no-header-row
    a,b,c,d
    1,2,3,4


::

    $ echo '1,2,3,4' | csvheader --add
    field_1,field_2,field_3,field_4
    1,2,3,4


.. note:: csvformat 1.0.6 bug

    In the latest official release of csvkit — 1.0.6 — csvformat's ``-H/--no-header-row`` does not work as expected. See issue/pull request `here <https://github.com/wireservice/csvkit/pull/1095>`_. (TODO: update this if csvkit master is patched)


Compared to listing column names with ``csvcut --names``
--------------------------------------------------------

TK Lorem ipsum dolor sit amet, consectetur adipisicing elit


::

    $ echo 'a,b, c ,d  ' | csvcut --names
      1: a
      2: b
      3:  c
      4: d


In contrast, because ``csvheader`` outputs the header as CSV, its output can be piped into, say, ``csvformat``, which, if you want, *can* produce quoted values to make the whitespace more obvious::


    $ echo 'a,b, c ,d  ' | csvheader | csvformat -U 1
    "index","field"
    "1","a"
    "2","b"
    "3"," c "
    "4","d  "


Compared to listing column names with ``xsv headers``
-----------------------------------------------------

::

    $ echo 'a,b, c ,d  ' | xsv headers
    1   a
    2   b
    3    c
    4   d


Compared to replacing the first line of data with ``sed``
---------------------------------------------------------

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


In contrast, ``csvheader --rename`` allows for renaming columns by (1-based) index::

    $ csvheader --rename '1|alpha,3|charlie' examples/heady.csv


    alpha, B Sharps ,charlie
    100,cats,Iowa
    200,dogs,Ohio








Common scenarios and use cases
==============================

TK TK


Adding a header to the Social Security babynames data
-----------------------------------------------------


The nationwide baby names data comes as a zip file of comma-delimited text files, one for each year, e.g. ``yob1880.txt`` and ``yob2015.txt``:

TK-IMG




Each file contains the same 3 columns — name, sex, and count — but *sans* header row. Here are the first 3 rows in ``yob1880.txt``::

    Mary,F,7065
    Anna,F,2604
    Emma,F,2003


Invoking ``csvheader`` with the ``-A/--add`` flag will add generic column names to the data of each individual file, e.g.::


    $ csvheader -A yob1880.txt
    field_1,field_2,field_3
    Mary,F,7065
    Anna,F,2604
    Emma,F,2003

    ...


But it's not much more work to add our own useful column names using the ``-C/--create`` option::

    $ csvheader yob1880.txt -C 'name,sex,count'
    name,sex,count
    Mary,F,7065
    Anna,F,2604
    Emma,F,2003



(TODONOTE: only when writing this example did I realize I should create this option; resume documentation writing here)


Of course, doing that for every file would be extremely tedious. You should be using ``csvstack`` with the ``-H/--no-header-row`` option to collate all the files into a single file and header::

    $ csvstack *.txt -H yob*.txt > babynames.csv

The more important reason to use ``csvstack`` is its ``--filenames`` option, which prepends a 'group' column to the data that contains the *filename* for each record::

    $ csvstack *.txt -H --filenames yob.txt > babynames.csv


This is *absolutely* critical, because the rows in each ``yob****.txt`` file don't include the year of the data file — which makes the compiled ``babynames.csv`` completely useless.

However, with ``csvstack --filenames``, that vital year context is included in the compiled ``babynames.csv``::

    group,a,b,c
    yob1880.txt,Mary,F,7065
    yob1880.txt,Anna,F,2604
    yob1880.txt,Emma,F,2003
    ...
    yob2018.txt,Zyrie,M,5
    yob2018.txt,Zyron,M,5
    yob2018.txt,Zzyzx,M,5


So where does TKTKTK
