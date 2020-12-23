**********
csvflatten
**********

:command:`csvflatten` is a command for producing "flattened" records. Useful for quickly getting a view of records with numerous fields, and for documenting data examples in Markdown-compatible format.

For example, given this ``data.csv``:

.. literalinclude:: ../../../examples/flatfruit.csv



— :command:`csvflatten` can be used to transform the data into a "narrow" 2-column denormalized format:


.. code-block:: shell

    $ csvflatten data.csv

.. code-block:: text


    | field       | value                                                 |
    | ----------- | ----------------------------------------------------- |
    | id          | 001                                                   |
    | product     | apples                                                |
    | price       | 1.50                                                  |
    | description | An apple is an edible fruit produced by an apple tree |
    |             | (Malus domestica)                                     |
    | ~~~~~~~~~~~ |                                                       |
    | id          | 002                                                   |
    | product     | oranges                                               |
    | price       | 2.25                                                  |
    | description | An orange is a type of citrus fruit that people often |
    |             | eat. Oranges are a very good source of vitamin C.     |



.. contents:: Table of contents
   :local:
   :depth: 3



.. include:: options.rstinc

.. include:: usage.rstinc


.. include:: real-usecases.rstinc

