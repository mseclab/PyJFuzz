#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
PyJFuzz trivial python fuzzer based on radamsa.

MIT License

Copyright (c) 2016 Daniele Linguaglossa <danielelinguaglossa@gmail.com>

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

import subprocess
import json
import random
import string
import gc
import urllib
import sys
import argparse

__version__ = 0.1
__author__ = "Daniele 'dzonerzy' Linguaglossa"
__mail__ = "danielelinguaglossa@gmail.com"


class JSONFactory:
    fuzz_factor = None
    was_array = None
    is_fuzzed = None

    def __init__(self):
        self.fuzz_factor = 0
        self.is_fuzzed = False
        self.was_array = False
        try:
            ver = subprocess.Popen(["radamsa", "-V"], stdout=subprocess.PIPE).communicate()[0]
            sys.stderr.write("[INFO] Using ({0})\n\n".format(ver.strip("\n")))
        except OSError:
            sys.stderr.write("[ERROR] Radamsa was not found, Please install it!\n\n")
            sys.exit(-1)

    def initWithJSON(self, json_obj):
        fuzz_factor = self.fuzz_factor
        try:
            self.__dict__ = json.loads(json_obj)
        except TypeError:
            self.__dict__ = json.loads("{\"array\": %s}" % json_obj)
            self.was_array = True
        except ValueError:
            self.__dict__ = {"dummy": "dummy"}
        self.fuzz_factor = fuzz_factor
        self.is_fuzzed = False

    def ffactor(self, factor):
        if factor not in range(0, 7):
            raise ValueError("Factor must be between 0-6")
        self.fuzz_factor = factor

    def fuzz(self):
        return self.fuzz_elements(self.__dict__, self.fuzz_factor)

    def fuzz_elements(self, elements, factor):
        if self.is_fuzzed:
            raise ValueError("You cannot fuzz an already fuzzed object please call 'initWithJSON'")
        self.is_fuzzed = True
        for element in elements.keys():
            if element in ["fuzz_factor", "was_array", "is_fuzzed"]:
                pass
            else:
                if type(elements[element]) == dict:
                    self.fuzz_elements(elements[element], factor)
                elif type(elements[element]) == list:
                    elements[element] = self.fuzz_array(elements[element], factor)
                elif type(elements[element]) == int:
                    elements[element] = self.fuzz_int(elements[element], factor)
                elif type(elements[element]) == bool:
                    elements[element] = self.fuzz_bool(elements[element], factor)
                elif type(elements[element]) == unicode:
                    elements[element] = self.fuzz_string(elements[element], factor)
                elif type(elements[element]) == str:
                    elements[element] = self.fuzz_string(elements[element], factor)
                elif elements[element] is None:
                    elements[element] = self.fuzz_null(factor)
        result = dict(self.__dict__)
        del result["fuzz_factor"]
        del result["is_fuzzed"]
        if self.was_array:
            del result["was_array"]
            return result["array"]
        return result

    def fuzz_null(self, factor):
        self.fuzz_factor = factor
        actions = {
            0: None,
            1: 0,
            2: False,
            3: [0],
            4: {},
            5: [0],
            6: {"null": 0}
        }
        return actions[random.randint(0, factor)]

    def fuzz_array(self, arr, factor):
        self.fuzz_factor = factor
        actions = {
            0: lambda x, y: x.append(str(y)),
            1: lambda x, y: x.append(self.fuzz_string(str(y), factor)),
            2: lambda x, y: x.append(["\\x00", "\\x00", "\\x00", "\\x00"]),
            3: lambda x, y: x.append(dict({})),
            4: lambda x, y: x.append(-1),
            5: lambda x, y: x.append(dict({self.fuzz_string("AAA", 0): [-1]})),
            6: lambda x, y: x.append(False)
        }
        choices = {
            1: lambda x: actions[random.randint(0, factor)](arr, arr.index(x)),
            2: lambda x: self.fuzz_string(str(arr[arr.index(x)]), factor),
            3: lambda x: x
        }
        for element in arr:
            if type(element) == str:
                arr[arr.index(element)] = self.fuzz_string(element, factor)
            if type(element) == unicode:
                arr[arr.index(element)] = self.fuzz_string(element, factor)
            elif type(element) == int:
                arr[arr.index(element)] = self.fuzz_int(element, factor)
            elif type(element) == bool:
                arr[arr.index(element)] = self.fuzz_bool(element, factor)
            elif element is None:
                arr[arr.index(element)] = self.fuzz_null(factor)
            else:
                arr[arr.index(element)] = choices[random.randint(1, 3)](element)
        return arr

    def fuzz_string(self, fuzz_string, factor):
        self.fuzz_factor = factor
        actions = {
            0: lambda x: x,
            1: lambda x: self.radamsa(x),
            2: lambda x: "",
            3: lambda x: [x],
            4: lambda x: False,
            5: lambda x: {"param": self.radamsa(x)},
            6: lambda x: 0,
        }
        return actions[random.randint(0, factor)](fuzz_string)

    def fuzz_bool(self, boolean, factor):
        self.fuzz_factor = factor
        actions = {
            0: lambda x: x,
            1: lambda x: not x,
            2: lambda x: str(x),
            3: lambda x: str(not x),
            4: lambda x: int(x),
            5: lambda x: int(not x),
            6: lambda x: float(x),
        }
        return actions[random.randint(0, factor)](boolean)

    def fuzz_int(self, num, factor):
        self.fuzz_factor = factor
        actions = {
            0: lambda x: x,
            1: lambda x: -x,
            2: lambda x: x*x,
            3: lambda x: x | 0xff,
            4: lambda x: random.randint(-2147483647, 2147483647),
            5: lambda x: bool(x),
            6: lambda x: x | 0xff000000
        }
        return actions[random.randint(0, factor)](num)

    def radamsa(self, to_fuzz):
        encodings = {
            0: lambda x: "\\x%02x" % ord(x),
            1: lambda x: urllib.quote(x),
            2: lambda x: urllib.quote(urllib.quote(x)),
            3: lambda x: "&#x%02x;" % ord(x),
        }
        attacks = {
            0: "javascript:alert(0);//",
            1: "http://",
            2: "/../../../../etc/passwd",
            3: "'or'1\"or'=\"'1--",
            4: "'\"><img src=0>",
            5: "||calc.exe;&&id|",
            6: "C:\\..\\",
            7: "--><img src=0>",
            8: "\"';]//)}//",
            9: ".\\",
            10: "./",
            11: "{${AAA}}",
            12: "{{13*37}}",
        }
        to_fuzz = attacks[random.randint(0, 6 + self.fuzz_factor)] + to_fuzz
        p1 = subprocess.Popen(['/bin/echo', to_fuzz], stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["radamsa"], stdin=p1.stdout, stdout=subprocess.PIPE)
        output = p2.communicate()[0]
        p1.stdout.close()
        p2.stdout.close()
        del p1
        del p2
        encode = encodings[random.randint(0, 3)]
        return "".join(encode(x) if x not in string.printable.strip("\t\n\r\x0b\x0c") else x for x in output)

if __name__ == "__main__":
    sys.stderr.write("PyJFuzz v{0} - {1} - {2}\n".format(__version__, __author__, __mail__))
    parser = argparse.ArgumentParser(description='Trivial Python JSON Fuzzer (c) DZONERZY')
    parser.add_argument('-j', metavar='JSON', help='Original JSON serialized object', required=True)
    parser.add_argument('-f', metavar='FUZZ_FACTOR', help='Fuzz factor [0-6]', type=int, default=6, required=False)
    parser.add_argument('-i', metavar='INDENT', help='JSON indent number', type=int, default=0, required=False)
    parser.add_argument('-ue', action='store_true', help='URLEncode result', dest='ue', default=False, required=False)
    args = parser.parse_args()
    obj = JSONFactory()
    obj.initWithJSON(args.j)
    obj.ffactor(args.f)
    if args.ue:
        sys.stdout.write(urllib.quote(json.dumps(obj.fuzz())))
    else:
        if args.i == 0:
            sys.stdout.write(json.dumps(obj.fuzz(), separators=(',', ':')))
        else:
            sys.stdout.write(json.dumps(obj.fuzz(), indent=args.i))
    gc.collect()
