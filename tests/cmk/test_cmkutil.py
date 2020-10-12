import re

import csvmedkit
import csvmedkit.__about__ as about
from csvmedkit.cmk.cmkutil import *

from tests.mk import TestCase, skiptest


class TestCMK(TestCase):
    def test_about(self):
        self.assertEqual("csvmedkit", about.__title__)

    def test_version(self):
        assert re.match(r"\d+\.\d+\.\d+", about.__version__)
