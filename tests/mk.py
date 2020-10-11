#!/usr/bin/env python

"""
Inherits the stuff from tests.csvk – i.e. csvkit.tests.utils
"""

from tests.csvk import *
from tests.csvk import CSVKitTestCase as BaseCsvkitTestCase

import unittest
from unittest.mock import patch
from unittest import skip as skiptest
from unittest import TestCase
import warnings

from csvmedkit import agate
from csvmedkit.exceptions import *


warnings.filterwarnings("ignore", category=DeprecationWarning)


class CmkTestCase(BaseCsvkitTestCase):
    pass
