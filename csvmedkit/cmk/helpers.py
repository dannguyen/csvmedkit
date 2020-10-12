"""Main module."""
import csv
from io import StringIO
import sys
from typing import (
    List as typeList,
    NoReturn as typeNoReturn,
    Iterable as typeIterable,
    Union as typeUnion,
    Sequence as typeSequence,
)

from slugify import slugify as pyslugify

from csvkit.grep import FilteringCSVReader

from csvmedkit import agate, parse_column_identifiers
from csvmedkit import re_std as re
from csvmedkit.exceptions import *


def cmk_parse_column_ids(
    ids: str, column_names: typeList[str], column_offset=1
) -> typeList[int]:
    """just a simplified version of parse_column_identifiers"""
    return parse_column_identifiers(
        ids, column_names, column_offset, excluded_columns=None
    )


def cmk_filter_rows(
    rows: typeIterable,
    pattern_str: str,
    columns_str: str,
    column_names: list,
    default_column_ids: list,
    literal_match: bool,
    column_offset: int,
    inverse: bool,
    any_match: bool,
    # not_columns,
) -> FilteringCSVReader:

    if literal_match:
        pattern = pattern_str
    else:  # literal match
        pattern = re.compile(pattern_str)

    if columns_str:
        expr_col_ids = parse_column_identifiers(
            columns_str,
            column_names,
            column_offset,
        )
    else:
        expr_col_ids = default_column_ids

    epatterns = dict((eid, pattern) for eid in expr_col_ids)

    filtered_rows = FilteringCSVReader(
        rows,
        header=False,
        patterns=epatterns,
        inverse=inverse,
        any_match=any_match,
    )
    return filtered_rows


def cmk_parse_delimited_str(
    txt: str,
    delimiter: str = ",",
    minlength: int = 0,
    escapechar=None,
    **csvreader_kwargs,
) -> typeList[typeUnion[str]]:
    """
    minlength: expected minimum number of elements. If csv.reader returns a row shorter than minlength, it
        will pad the row with empty strings ''
    """
    row: typeList
    with StringIO(txt) as src:
        kwargs = csvreader_kwargs.copy()
        kwargs["delimiter"] = delimiter
        kwargs["escapechar"] = escapechar

        data = csv.reader(src, **kwargs)
        row = next(data, [])

    for i in range(len(row), minlength):
        row.append("")

    return row


def cmk_slugify(txt: typeUnion[str, typeSequence]) -> str:
    if not isinstance(txt, str):
        # e.g a list of strings
        txt = " ".join(txt)
    return pyslugify(txt, separator="_")
