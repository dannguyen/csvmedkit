#!/usr/bin/env python

"""
Copies csvkit's init plus some other things
"""

from csvkit import agate


#  from csvkit import reader, writer, DictReader, DictWriter
from csvkit.cli import CSVKitUtility, parse_column_identifiers
from csvmedkit.__about__ import __title__, __version__, __description__

import re as re_std  # because I'm still deciding between re/regex, we should have a global reference to the lib
import regex as re_plus


from typing import Union as UnionType, Sequence as SequenceType

agate = agate
rxlib = re_std
