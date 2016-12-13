"""
The MIT License (MIT)

Copyright (c) 2016 Daniele Linguaglossa <d.linguaglossa@mseclab.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from pyjfuzz.core.pjf_configuration import PJFConfiguration
import unittest
import argparse
import sys


__TITLE__ = "Testing PJFConfiguration object"

class TestPJFConfiguration(unittest.TestCase):

    def test_json_configuration(self):
        sys.argv.append("--J")
        sys.argv.append("[1]")
        sys.argv.append("--no-logo")
        parser = argparse.ArgumentParser(description='', formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument('--J', type=str, default=None)
        parser.add_argument('--no-logo', action='store_true', dest='nologo', default=False, required=False)
        parsed = parser.parse_args()
        args = PJFConfiguration(parsed)
        for arg in parsed.__dict__:
            self.assertTrue(arg in args.__dict__)


def test():
    print "=" * len(__TITLE__)
    print __TITLE__
    print "=" * len(__TITLE__)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPJFConfiguration)
    unittest.TextTestRunner(verbosity=2).run(suite)

