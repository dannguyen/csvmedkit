**********
csvflatten
**********

.. contents:: :local:


Description
===========

Print records in column-per-line format. Best used in conjunction with `csvlook <https://csvkit.readthedocs.io/en/latest/scripts/csvlook.html>`_

Similar in concept to `xsv flatten <https://github.com/BurntSushi/xsv#available-commands>`_, though the output is much different.

TK/TODO: copy text/rationale from `original Github issue <https://github.com/dannguyen/csvkit/issues/1>`_



Example::

    $ csvflatten examples/hamlet.csv --prettify

    | fieldname | value                                          |
    | --------- | ---------------------------------------------- |
    | act       | 1                                              |
    | scene     | 5                                              |
    | speaker   | Horatio                                        |
    | lines     | Propose the oath, my lord.                     |
    | ~~~~~~~~~ |                                                |
    | act       | 1                                              |
    | scene     | 5                                              |
    | speaker   | Hamlet                                         |
    | lines     | Never to speak of this that you have seen,     |
    |           | Swear by my sword.                             |
    | ~~~~~~~~~ |                                                |
    | act       | 1                                              |
    | scene     | 5                                              |
    | speaker   | Ghost                                          |
    | lines     | [Beneath] Swear.                               |
    | ~~~~~~~~~ |                                                |
    | act       | 3                                              |
    | scene     | 4                                              |
    | speaker   | Gertrude                                       |
    | lines     | O, speak to me no more;                        |
    |           | These words, like daggers, enter in mine ears; |
    |           | No more, sweet Hamlet!                         |
    | ~~~~~~~~~ |                                                |
    | act       | 4                                              |
    | scene     | 7                                              |
    | speaker   | Laertes                                        |
    | lines     | Know you the hand?                             |



Comparison to existing tools
============================


``csvlook`` doesn't pretty-format multi-line fields, and can also result in very wide tables without ``--max-column-width``::

    $ csvlook examples/hamlet.csv --max-column-width 50

    | act | scene | speaker  | lines                                              |
    | --- | ----- | -------- | -------------------------------------------------- |
    |   1 |     5 | Horatio  | Propose the oath, my lord.                         |
    |   1 |     5 | Hamlet   | Never to speak of this that you have seen,
    Swea... |
    |   1 |     5 | Ghost    | [Beneath] Swear.                                   |
    |   3 |     4 | Gertrude | O, speak to me no more;
    These words, like dagge... |
    |   4 |     7 | Laertes  | Know you the hand?                                 |


``xsv flatten`` does do auto-wrapping of long entries, but doesn't produce tableized output::

    $ xsv flatten examples/hamlet.csv

    act      1
    scene    5
    speaker  Horatio
    lines    Propose the oath, my lord.
    #
    act      1
    scene    5
    speaker  Hamlet
    lines    Never to speak of this that you have seen,
    Swear by my sword.
    #
    act      1
    scene    5
    speaker  Ghost
    lines    [Beneath] Swear.
    #
    act      3
    scene    4
    speaker  Gertrude
    lines    O, speak to me no more;
    These words, like daggers, enter in mine ears;
    No more, sweet Hamlet!
    #
    act      4
    scene    7
    speaker  Laertes
    lines    Know you the hand?
