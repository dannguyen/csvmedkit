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

from io import StringIO
from parameterized import parameterized
from subprocess import Popen, PIPE  # soon to be deprecated
from subprocess import check_output as sub_check_output
import sys
from typing import List as ListType, Optional as OptionalType

from csvmedkit import agate
from csvmedkit.exceptions import *


warnings.filterwarnings("ignore", category=DeprecationWarning)


class CmkTestCase(BaseCsvkitTestCase):
    def cmd_output(self, command: str) -> str:
        output = sub_check_output(command, shell=True, stderr=sys.stderr)
        return output.decode("utf-8")

    def assertCmdLines(self, command: str, rows, newline_at_eof=True):
        lines = self.cmd_output(command).split("\n")

        if newline_at_eof:
            rows.append("")

        for i, row in enumerate(rows):
            self.assertEqual(lines[i], row)

        self.assertEqual(len(lines), len(rows))

    # TODO: probably will deprecate pipe_output and assertPipedLines for being too
    # clunky for my tastes
    def pipe_output(self, commands: ListType[str]) -> OptionalType[str]:
        """
        each command is a list of strings, representing a command and argument, e.g.
            ['head', '-n', '5', 'examples/dummy.csv'],
            ['csvflatten', '-P'],
        """
        output = None  # StringIO()
        cmdcount = len(commands)
        pipes = []
        for i, cmd in enumerate(commands, 1):
            if i == 1:
                p = Popen(cmd, stdout=PIPE)
            elif i == cmdcount:
                pass  # manually instantiate last command with context manager
            else:
                p = Popen(cmd, stdin=pipes[-1].stdout, stdout=PIPE)
            pipes.append(p)

        with Popen(commands[-1], stdin=pipes[-1].stdout, stdout=PIPE) as foo:
            output = foo.communicate()[0].decode("utf-8")
            foo.kill()

        # pipes[0].stdout.close()
        for p in pipes:
            p.wait()
            p.stdout.close()
            # p.kill()

        return output

    def pipe_output_as_list(self, commands) -> ListType[str]:
        return self.pipe_output(commands).split("\n")

    def assertPipedLines(self, commands, rows, newline_at_eof=True):
        lines = self.pipe_output_as_list(commands)

        if newline_at_eof:
            rows.append("")

        for i, row in enumerate(rows):
            self.assertEqual(lines[i], row)

        self.assertEqual(len(lines), len(rows))
