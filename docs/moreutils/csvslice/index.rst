********
csvslice
********

:command:`csvslice` is a command for selecting rows by 0-based index and/or inclusive ranges.


Given :download:`example.csv`:


.. code-block:: shell

    $ csvslice -i 0,2-3 example.csv
    id,val
    a,0
    c,2
    d,3


.. contents:: Table of contents
   :local:
   :depth: 3




.. include:: options.rstinc

.. include:: usage.rstinc

.. include:: comparison.rstinc







Real-world use cases
====================

.. include:: /scenarios/acs-csvslice-skip-meta.rstinc
