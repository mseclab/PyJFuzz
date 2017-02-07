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
from argparse import Namespace
import unittest
import urllib2


from pyjfuzz.core.pjf_server import PJFServer

__TITLE__ = "Testing PJFFServer Object"

class TestPJFServer(unittest.TestCase):

    def test_start_object(self):
        server = PJFServer(configuration=PJFConfiguration(Namespace(ports={"servers": {"HTTP_PORT": 8080, "HTTPS_PORT": 8443}},
                                                   html=False, level=6, command=["radamsa"], stdin=True,
                                                   json={"a": "test"}, indent=True, strong_fuzz=False, url_encode=False,
                                                   parameters=[], notify=False, debug=False, content_type="text/plain",
                                                                    utf8=False, nologo=True)))
        server.run()
        json_http = urllib2.urlopen("http://127.0.0.1:8080").read()
        try:
            import requests
            requests.packages.urllib3.disable_warnings()
            json_https = requests.get('https://127.0.0.1:8443', verify=False).content
            self.assertTrue(json_https)
        except ImportError:
            pass
        self.assertTrue(json_http)
        server.stop()


def test():
    print "=" * len(__TITLE__)
    print __TITLE__
    print "=" * len(__TITLE__)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPJFServer)
    unittest.TextTestRunner(verbosity=2).run(suite)

