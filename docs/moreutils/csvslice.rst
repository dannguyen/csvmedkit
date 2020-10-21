********
csvslice
********

:command:`csvslice` TKTK

TK TK TK  Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod


.. contents:: Table of contents
   :local:
   :depth: 3




Usage reference
===============


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




Note: this is a required option



High level overview
===================

Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
proident, sunt in culpa qui officia deserunt mollit anim id est laborum.



How csvslice compares to existing tools
=======================================


head/tail
---------

xsv slice
---------

TK



Agate
-----

TK


pandas
------










Usecases
========

TK
