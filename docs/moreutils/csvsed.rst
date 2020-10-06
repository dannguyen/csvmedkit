******
csvsed
******

.. contents:: :local:


Description
===========

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
