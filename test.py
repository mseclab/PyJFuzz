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
FITNESS FOR A PARTICULAR PURPOSE AND NON INFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from test import test_pjf_factory
from test import test_pjf_process_monitor
from test import test_pjf_mutation
from test import test_pjf_external_fuzzer
from test import test_pjf_encoder
from test import test_pjf_configuration
from test import test_pjf_server
from test import test_pjf_environment

if __name__ == "__main__":
    print("PyJFuzz - Test Unit")
    print("[INFO] Starting tests...\n\n")
    test_pjf_environment.test()
    test_pjf_factory.test()
    test_pjf_mutation.test()
    test_pjf_external_fuzzer.test()
    test_pjf_configuration.test()
    test_pjf_server.test()
    test_pjf_encoder.test()
    test_pjf_process_monitor.test()
