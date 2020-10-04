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
