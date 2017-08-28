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
from errors import PJFInvalidType, PJFMissingArgument, PJFBaseException
from pjf_mutators import PJFMutators
from pjf_mutation import PJFMutation
from pjf_encoder import PJFEncoder
from pjf_logger import PJFLogger
import time
import json
import urllib

class PJFFactory(object):

    def __init__(self, configuration):
        """
        Class that represent a JSON object
        """
        self.logger = self.init_logger()
        if ["json", "json_file", "strong_fuzz", "parameters", "exclude_parameters", "url_encode", "indent",
                "utf8"] not in configuration:
            raise PJFMissingArgument("Some arguments are missing from PJFFactory object")

        self.config = configuration
        self.mutator = PJFMutation(self.config)
        other = self.config.json
        if not self.config.strong_fuzz:
            if type(other) == dict:
                self.json = other
            elif type(other) == list:
                self.json = {"array": other}
            else:
                raise PJFInvalidType(other, dict)
        else:
            if self.config.json_file:
                self.json = other
            else:
                self.json = json.dumps(other)
        self.logger.debug("[{0}] - PJFFactory successfully initialized".format(time.strftime("%H:%M:%S")))

    def __add__(self, other):
        """
        Add keys to dictionary merging with another dictionary object
        """
        self.json.update(other)
        return self

    def __sub__(self, other):
        """
        Removes keys from self dictionary based on provided list
        """
        if type(other) == list:
            for element in other:
                if element in self.json:
                    del self.json[element]
            return self
        else:
            raise PJFInvalidType(other, list)

    def __eq__(self, other):
        """
        Check if two object are equal
        """
        return self.json == other

    def __getitem__(self, item):
        """
        Extract an item from the JSON object
        """
        if type(item) == str:
            return self.json[item]
        else:
            return self.json

    def __setitem__(self, key, value):
        """
        Set a JSON attribute
        """
        self.json[key] = value

    def __contains__(self, items):
        """
        Check if JSON object contains a key
        """
        try:
            if type(items) != list:
                raise PJFInvalidType(items, list)
            ret = 0
            for item in items:
                for key in self.json:
                    if isinstance(self.json[key], PJFFactory):
                        ret += item in self.json[key]
                    elif item == key:
                        ret += 1
            return len(items) == ret
        except Exception as e:
            raise PJFBaseException(e.message)

    def __repr__(self):
        """
        Represent the JSON object
        """
        return str(self.json)

    def fuzz_elements(self, element):
        """
        Fuzz all elements inside the object
        """
        try:
            if type(element) == dict:
                tmp_element = {}
                for key in element:
                    if self.config.parameters:
                        if self.config.exclude_parameters:
                            fuzz = key not in self.config.parameters
                        else:
                            fuzz = key in self.config.parameters
                    else:
                        fuzz = True
                    if fuzz:
                        if type(element[key]) == dict:
                            tmp_element.update({key: self.fuzz_elements(element[key])})
                        elif type(element[key]) == list:
                            tmp_element.update({key: self.fuzz_elements(element[key])})
                        else:
                            tmp_element.update({key: self.mutator.fuzz(element[key])})
                    else:
                        tmp_element.update({key: self.fuzz_elements(element[key])})
                element = tmp_element
                del tmp_element
            elif type(element) == list:
                arr = []
                for key in element:
                    if type(key) == dict:
                        arr.append(self.fuzz_elements(key))
                    elif type(key) == list:
                        arr.append(self.fuzz_elements(key))
                    else:
                        arr.append(self.mutator.fuzz(key))
                element = arr
                del arr
        except Exception as e:
            raise PJFBaseException(e.message)
        return element

    def init_logger(self):
        """
        Init the default logger
        """
        return PJFLogger.init_logger()

    @property
    def fuzzed(self):
        """
        Get a printable fuzzed object
        """
        try:
            if self.config.strong_fuzz:
                fuzzer = PJFMutators(self.config)
                if self.config.url_encode:
                    return urllib.quote(fuzzer.fuzz(json.dumps(self.config.json)))
                else:
                    if type(self.config.json) in [list, dict]:
                        return fuzzer.fuzz(json.dumps(self.config.json))
                    else:
                        return fuzzer.fuzz(self.config.json)
            else:
                if self.config.url_encode:
                    return urllib.quote(self.get_fuzzed(self.config.indent, self.config.utf8))
                else:
                    return self.get_fuzzed(self.config.indent, self.config.utf8)
        except Exception as e:
            raise PJFBaseException(e.message)

    @PJFEncoder.json_encode
    def get_fuzzed(self, indent=False, utf8=False):
        """
        Return the fuzzed object
        """
        try:
            if "array" in self.json:
                return self.fuzz_elements(dict(self.json))["array"]
            else:
                return self.fuzz_elements(dict(self.json))
        except Exception as e:
            raise PJFBaseException(e.message)
