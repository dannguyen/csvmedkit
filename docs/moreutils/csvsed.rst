******
csvsed
******

:command:`csvsed` is a command to do find-and-replace on a per-column basis.

Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
proident, sunt in culpa qui officia deserunt mollit anim id est laborum.




Usage reference
===============



-c, --columns <columns_list>
----------------------------

TK A comma separated list of column indices, names or ranges to be affected, e.g. "1,id,3-5". If not specified, csvsed will affect *all* columns

-m, --match-literal
-------------------

TK By default, [PATTERN] is assumed to be a regex. Set this flag to make it a literal text find/replace


-G, --like-grep
---------------

TK: Only return rows in which [PATTERN] was a match (BEFORE any transformations) – i.e. like grep''s traditional behavior


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
