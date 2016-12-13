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
from pyjfuzz.core.pjf_external_fuzzer import PJFExternalFuzzer
from pyjfuzz.core.pjf_configuration import PJFConfiguration
from argparse import Namespace
import unittest
import os

__TITLE__ = "Testing PJFExternalFuzzer object"

class TestPJFExternalFuzzer(unittest.TestCase):

    def test_string_mutation(self):
        external_fuzzer = PJFExternalFuzzer(PJFConfiguration(Namespace(nologo=True, command=["radamsa"], stdin=True)))
        mutated = external_fuzzer.execute("MUTATION_EXAMPLE")
        self.assertTrue(len(mutated) > 0)

    def test_file_mutation(self):
        external_fuzzer = PJFExternalFuzzer(PJFConfiguration(Namespace(nologo=True, command=["radamsa","@@"],
                                                                       stdin=False)))
        with file("test.json", "wb") as json_file:
            json_file.write('{"a": 1}')
            json_file.close()
        external_fuzzer.execute("test.json")
        with file("test.json", "rb") as json_file:
            content = json_file.read()
            json_file.close()
            self.assertTrue(len(content) > 0)
        os.unlink("test.json")

def test():
    print "=" * len(__TITLE__)
    print __TITLE__
    print "=" * len(__TITLE__)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPJFExternalFuzzer)
    unittest.TextTestRunner(verbosity=2).run(suite)
