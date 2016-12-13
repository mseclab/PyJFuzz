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
from pyjfuzz.core.pjf_process_monitor import PJFProcessMonitor
from pyjfuzz.core.pjf_configuration import PJFConfiguration
from argparse import Namespace
from test import TEST_PATH
import subprocess
import unittest
import os

__TITLE__ = "Testing PJFProcessMonitor object"

class TestPJFProcessMonitor(unittest.TestCase):

    def test_process_monitor(self):
        os.chdir(TEST_PATH)
        subprocess.Popen(["gcc", "sigsegv.c", "-o", "sigsegv"], stderr=subprocess.PIPE, stdout=subprocess.PIPE).wait()
        crash = PJFProcessMonitor(PJFConfiguration(Namespace(process_to_monitor=["%s/sigsegv" % TEST_PATH], debug=False,
                                            ports={"servers":
                                                       {
                                                           "HTTP_PORT": 8080,
                                                           "HTTPS_PORT": 8443,
                                                           "TCASE_PORT": 8888
                                                       }
                                            },
                                                             nologo=True))
                                  ).run_and_monitor()
        self.assertTrue(crash)

def test():
    print "=" * len(__TITLE__)
    print __TITLE__
    print "=" * len(__TITLE__)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPJFProcessMonitor)
    unittest.TextTestRunner(verbosity=2).run(suite)

