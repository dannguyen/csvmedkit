**********
csvheaders
**********

.. contents:: :local:


Description
===========

Get a list of headers, and/or transform the headers, e.g. rename and/or slugify them:


Example::

    $ csvheaders examples/TK.csv --slugify



Similar to using `to replace the first line <https://superuser.com/a/1026686>`_, e.g.::

    $ sed -i '1s/.*/field_1,field_2,field_3/' data.csv


-- except that ``sed`` will not work on multi-line headers. And ``sed`` can't be used to selectively rename headers by name/index::

    $ csvheaders examples/dummy.csv --rename 'a|apples,c|cherries'


::

    apples,b,cherries
    1,2,3
