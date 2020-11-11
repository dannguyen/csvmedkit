=========
csvmedkit
=========

The unofficial extended family of csvkit, i.e. even more tools for command-line data parsing and wrangling.

**Status as of 2020-11-11**: Alpha, but working toward release version with these utilities:


- csvflatten: reformat data for easier browsing of "wide" data
- csvheader: add/alter a data file's column names
- csvnorm: normalize unprintable characters and whitespace
- csvpivot: do pivot tables
- csvsed: do sed substitution on a per-column basis
- csvslice: return rows by index, including head/tail to get first/last n rows


Read the in-progress docs at: `csvmedkit.readthedocs.io <https://csvmedkit.readthedocs.io/>`_



- Read TODOS: `TODOS.md <TODOS.md>`_ for an informal roadmap.
- The old, now archived csvkitcat repo: `dannguyen/csvkitcat <https://github.com/dannguyen/csvkitcat>`_


Note: many of the data examples incorporate the original csvkit tools, including a couple of post 1.0.6 fixes. Until csvkit makes a new official release, here's what I used::


    $ pip install git+https://github.com/wireservice/csvkit.git@73d5bdc4a2f5c07b91737ea007bb3510f970aad7
