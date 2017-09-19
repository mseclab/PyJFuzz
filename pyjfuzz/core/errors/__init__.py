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
import sys

class PJFBaseException(Exception):

    err_type = "ERROR"

    def __str__(self):
        if not hasattr(self,"message"):
            self.message = self.args[0]
        self.__class__.__module__ = "[\033[91m%s\033[0m]: %s" % (self.err_type, self.message)
        self.__class__.__name__ = ""
        return ""

class PJFEnvironmentError(PJFBaseException):
    """
    Environment error e.g. missing dependencies
    """
    err_type = "ENVIRONMENT ERROR"

class PJFProcessError(PJFBaseException):
    """
    Environment error e.g. missing dependencies
    """
    err_type = "PROCESS ERROR"

class PJFMissingDependency(PJFEnvironmentError):
    """
    Missing dependency
    """
    err_type = "MISSING DEPENDENCY"

class PJFInvalidArgument(PJFBaseException):
    """
    Invalid argument passed to PyJFuzz
    """
    err_type = "INVALID ARGUMENT"

class PJFInvalidJSON(PJFBaseException):
    """
    Invalid argument passed to PyJFuzz
    """
    err_type = "INVALID JSON"

class PJFSocketError(PJFBaseException):
    """
    Socket issue
    """
    err_type = "SOCKET ERROR"

class PJFMissingArgument(PJFInvalidArgument):
    """
    Invalid argument due to object type
    """
    err_type = "MISSING ARGUMENT"


class PJFInvalidType(PJFInvalidArgument):
    """
    Invalid argument due to object type
    """
    err_type = "INVALID TYPE"

    def __init__(self, obj, expected):
        self.message = "Invalid object type ({0}) expecting ({1})".format(type(obj).__name__, expected.__name__)
        super(PJFInvalidType, self).__init__(self.message, None)


class PJFSocketPortInUse(PJFSocketError):
    """
    Socket port already in use
    """
    err_type = "SOCKET ERROR"


class PJFProcessExecutionError(PJFProcessError):
    """
    Error during process execution
    """

class PJFMalformedJSON(PJFInvalidJSON):
    """
    Invalid argument passed to PyJFuzz
    """
    err_type = "MALFORMED JSON"

    def __init__(self):
        self.message = "Invalid JSON object"