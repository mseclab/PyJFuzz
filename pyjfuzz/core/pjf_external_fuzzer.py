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
from .pjf_executor import PJFExecutor
from .errors import PJFMissingArgument, PJFBaseException
import time


class PJFExternalFuzzer(PJFExecutor):
    """
    Represent an instance of an external command line fuzzer
    """

    def __init__(self, configuration):
        """
            Init the class with fuzzer name (command), a boolean that represent whenever the fuzzer
            accept arguments form stdin, otherwise specify a command line. The special keyword "@@"
            will be replaced with the content of argument to fuzz
        """
        self.logger = self.init_logger()
        if ["command"] not in configuration:
            raise PJFMissingArgument()
        self.fuzzer = None
        self.config = configuration
        super(PJFExternalFuzzer, self).__init__(configuration)
        self.logger.debug("[{0}] - PJFExternalFuzzer successfully initialized".format(time.strftime("%H:%M:%S")))

    def execute_sigsegv(self, obj):
        self.execute(obj)
        self.logger.debug("[{0}] - PJFExternalFuzzer successfully completed".format(time.strftime("%H:%M:%S")))
        return self.return_code in [-11, -6, -1]

    def execute(self, obj):
        """
        Perform the actual external fuzzing, you may replace this method in order to increase performance
        """
        try:
            if self.config.stdin:
                    self.spawn(self.config.command, stdin_content=obj, stdin=True, timeout=1)
            else:
                if "@@" not in self.config.command:
                    raise PJFMissingArgument("Missing @@ filename indicator while using non-stdin fuzzing method")
                for x in self.config.command:
                    if "@@" in x:
                        self.config.command[self.config.command.index(x)] = x.replace("@@", obj)
                self.spawn(self.config.command, timeout=2)
            self.logger.debug("[{0}] - PJFExternalFuzzer successfully completed".format(time.strftime("%H:%M:%S")))
            return self._out
        except KeyboardInterrupt:
            return ""
        except Exception as e:
            raise PJFBaseException(e.message if hasattr(e, "message") else str(e))
