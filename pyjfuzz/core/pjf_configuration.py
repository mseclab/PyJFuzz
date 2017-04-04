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
import os
import sys
import json
import socket
from ast import literal_eval
from conf import CONF_PATH
from argparse import Namespace
from pjf_version import PYJFUZZ_LOGO
from pjf_grammar import generate_json
from . import GRAMMAR_PATH
from errors import PJFInvalidType

class PJFConfiguration(Namespace):
    """
    A class that represent PyJFuzz startup configuration , it makes the standard checks
    """
    def __init__(self, arguments):
        """
        Init the command line
        """
        super(PJFConfiguration, self).__init__(**arguments.__dict__)
        setattr(self, "generate_json", generate_json)
        setattr(self, "grammar_path", GRAMMAR_PATH)
        if self.json:
            if type(self.json) != dict:
                if type(self.json) != list:
                    raise PJFInvalidType(self.json, dict)
        if self.level:
            if type(self.level) != int:
                raise PJFInvalidType(self.level, int)
        if self.techniques:
            if type(self.techniques) != str:
                raise PJFInvalidType(self.techniques, str)
        if self.command:
            if type(self.command) != list:
                raise PJFInvalidType(self.command, list)
        if self.parameters:
            if type(self.parameters) != str:
                raise PJFInvalidType(self.parameters, str)
        if not self.nologo:
            sys.stderr.write("{0}\n".format(PYJFUZZ_LOGO))
        if self.recheck_ports:
            if self.fuzz_web or self.web_server or self.browser_auto:
                with open(CONF_PATH, "rb") as config:
                    setattr(self, "ports", self.check_ports(json.loads(config.read())))
                    config.close()
        if self.parameters:
            self.parameters = str(self.parameters).split(",")
        if self.techniques:
            techniques = {
                "C": [10, 5, 13],
                "H": [9],
                "P": [6, 2, 8],
                "T": [11, 12],
                "R": [14],
                "S": [3, 1],
                "X": [0, 4, 7]
            }
            temp = []
            for technique in self.techniques:
                if technique in techniques:
                    temp += techniques[str(technique)]
            self.techniques = temp
        else:
            self.techniques = range(0, 14)
        if not self.utf8:
            self.utf8 = False
        if not self.command:
            self.command = ["echo"]
            self.stdin = True
        else:
            if "@@" in self.command:
                self.stdin = False
            else:
                self.stdin = True
        if not self.parameters:
            self.parameters = []
        if self.auto:
            self.json = self.generate_json(self.grammar_path)

    def __contains__(self, items):
        if type(items) != list:
            raise PJFInvalidType(type(items), list)
        for element in items:
            try:
                getattr(self, element)
            except AttributeError:
                return False
        return True

    def __getattr__(self, item):
        """
        Get a parameter from configuration, return False if parameter was not found
        """
        if item in self.__dict__:
            return self.__dict__[item]
        else:
            if item == "recheck_ports":
                return True
            return False

    def start(self):
        """
        Parse the command line and start PyJFuzz
        """
        from pjf_worker import PJFWorker
        worker = PJFWorker(self)
        if self.update_pjf:
            worker.update_library()
        elif self.browser_auto:
            worker.browser_autopwn()
        elif self.fuzz_web:
            worker.web_fuzzer()
        elif self.json:
            if not self.web_server and not self.ext_fuzz and not self.cmd_fuzz:
                worker.fuzz()
            elif self.ext_fuzz:
                if self.stdin:
                    worker.fuzz_stdin()
                else:
                    worker.fuzz_command_line()
            elif self.cmd_fuzz:
                if self.stdin:
                    worker.fuzz_external(True)
                else:
                    worker.fuzz_external()
            else:
                worker.start_http_server()
        elif self.json_file:
            worker.start_file_fuzz()
        elif self.process_to_monitor:
            worker.start_process_monitor()

    def check_ports(self, ports):
            for p in ports["servers"]:
                try:
                    p_checker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    p_checker.bind(("127.0.0.1", ports["servers"][p]))
                    p_checker.close()
                except socket.error as e:
                    if e.errno == 48:
                        print "[\033[92mINFO\033[0m] Port %s is already in use switching to different port" % \
                              ports["servers"][p]
                        ports["servers"][p] = self.get_free_port()
            return ports

    def get_free_port(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('127.0.0.1', 0))
        port = s.getsockname()[1]
        s.close()
        return port

    @staticmethod
    def valid_dir(value):
        import argparse
        parser = argparse.ArgumentParser()
        if os.path.isdir(value):
            return value
        else:
            raise parser.error("Directory does not exists!")

    @staticmethod
    def valid_file(value):
        import argparse
        parser = argparse.ArgumentParser()
        try:
            with open(value, "rb") as html_file:
                html_file.close()
                return value
        except IOError:
            raise parser.error("File does not exists!")

    @staticmethod
    def valid_json(value):
        import argparse
        parser = argparse.ArgumentParser()
        try:
            try:
                value = literal_eval(value)
            except:
                value = json.loads(value)
            if type(value) not in (dict, list):
                raise SyntaxError
        except SyntaxError:
            raise parser.error("Please insert a valid JSON value!")
        return value
