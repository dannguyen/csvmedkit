#!/usr/bin/env python

"""
Copies csvkit's init plus some other things
"""

from csvkit import agate

agate = agate

#  from csvkit import reader, writer, DictReader, DictWriter
from csvkit.cli import CSVKitUtility, parse_column_identifiers
from csvmedkit.__about__ import __title__, __version__, __description__


from slugify import slugify as pyslugify
from typing import Union as tyUnion, Sequence as tySequence

import re as re_std  # because I'm still deciding between re/regex, we should have a global reference to the lib

rxlib = re_std

import regex as re_plus


def slugify(txt: tyUnion[str, tySequence]) -> str:
    if not isinstance(txt, str):
        txt = " ".join(txt)
    return pyslugify(txt, separator="_")
