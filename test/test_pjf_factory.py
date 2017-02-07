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
from pyjfuzz.core.pjf_factory import PJFFactory
from argparse import Namespace
import unittest

__TITLE__ = "Testing PJFFactory Object"

class TestPJFFactory(unittest.TestCase):

    def test_nested_object(self):
        self.assertTrue(PJFFactory(PJFConfiguration(Namespace(utf8=False, url_encode=False, parameters=None,
                                                              strong_fuzz=False, json={"t": 1, "foo": {"cow": True}},
                                                              nologo=True, techniques="CHPTRSX"))))

    def test_object_addition(self):
        json = PJFFactory(PJFConfiguration(Namespace(utf8=False, url_encode=False, parameters=None, strong_fuzz=False,
                                                     json={"a": 1}, nologo=True, techniques="CHPTRSX")))
        json += {"foo": True}
        self.assertTrue(json["foo"])

    def test_object_equal(self):
        json = PJFFactory(PJFConfiguration(Namespace(utf8=False, url_encode=False, parameters=None, strong_fuzz=False,
                                                     json={"a": 1}, nologo=True, techniques="CHPTRSX")))
        self.assertEquals(json, {"a": 1})
        self.assertNotEqual(json, {"a": 0})

    def test_object_contains(self):
        json = PJFFactory(PJFConfiguration(Namespace(utf8=False, url_encode=False, parameters=None, strong_fuzz=False,
                                                     json={"a": 1}, nologo=True, techniques="CHPTRSX")))
        self.assertTrue(["a"] in json)
        self.assertFalse(["A"] in json)

    def test_object_setitem(self):
        json = PJFFactory(PJFConfiguration(Namespace(utf8=False, url_encode=False, parameters=None, strong_fuzz=False,
                                                     json={"a": False}, nologo=True, techniques="CHPTRSX")))
        json["a"] = True
        self.assertTrue(json["a"])

    def test_object_representation(self):
        json = PJFFactory(PJFConfiguration(Namespace(utf8=False, url_encode=False, parameters=None, strong_fuzz=False,
                                                     json={"a": 1}, nologo=True, techniques="CHPTRSX")))
        self.assertTrue(str(json) == "{'a': 1}")
        self.assertTrue(type(str(json)) == str)

    def test_object_fuzz(self):
        json = PJFFactory(PJFConfiguration(Namespace(utf8=False, url_encode=False, parameters=None, strong_fuzz=False,
                                                     json={"a": "\xf0aaaaaaa"}, command=["radamsa"], stdin=True, level=6,
                                                     indent=True, nologo=True)))
        self.assertTrue(json.fuzzed)


def test():
    print "=" * len(__TITLE__)
    print __TITLE__
    print "=" * len(__TITLE__)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPJFFactory)
    unittest.TextTestRunner(verbosity=2).run(suite)

