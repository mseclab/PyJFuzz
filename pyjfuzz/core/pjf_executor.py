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

from .errors import PJFInvalidType, PJFProcessExecutionError, PJFBaseException
from threading import Thread
from subprocess import PIPE
from .pjf_logger import PJFLogger
from select import error
import subprocess
import signal
import time
import sys

class PJFExecutor(object):
    """
    Main class used to spawn and kill processes
    """

    def __init__(self, arg=None):
        """
        Init the main class
        """
        self.logger = self.init_logger()
        self.process = None
        self._out = ""
        self.return_code = 0
        self._in = ""
        self.logger.debug("[{0}] - PJFExecutor successfully initialized".format(time.strftime("%H:%M:%S")))

    def spawn(self, cmd, stdin_content="", stdin=False, shell=False, timeout=2):
        """
        Spawn a new process using subprocess
        """
        try:
            if type(cmd) != list:
                raise PJFInvalidType(type(cmd), list)
            if type(stdin_content) != str:
                raise PJFInvalidType(type(stdin_content), str)
            if type(stdin) != bool:
                raise PJFInvalidType(type(stdin), bool)
            self._in = stdin_content
            try:
                self.process = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE, stdin=PIPE, shell=shell)
                self.finish_read(timeout, stdin_content, stdin)
                if self.process.poll() is not None:
                    self.close()
            except KeyboardInterrupt:
                return
        except OSError:
            raise PJFProcessExecutionError("Binary <%s> does not exist" % cmd[0])
        except Exception as e:
            raise PJFBaseException(e.message if hasattr(e, "message") else str(e))

    def get_output(self, stdin_content, stdin):
        """
        Try to get output in a separate thread
        """
        try:
            if stdin:
                if sys.version_info >= (3, 0):
                    self.process.stdin.write(bytes(stdin_content, "utf-8"))
                else:
                    self.process.stdin.write(stdin_content)
            self._out = self.process.communicate()[0]
        except (error, IOError):
            self._out = self._in
            pass

    def finish_read(self, timeout=2, stdin_content="", stdin=False):
        """
        Wait until we got output or until timeout is over
        """
        process = Thread(target=self.get_output, args=(stdin_content, stdin))
        process.start()
        if timeout > 0:
            process.join(timeout)
        else:
            process.join()
        if process.is_alive():
            self.close()
            self.return_code = -signal.SIGHUP
        else:
            self.return_code = self.process.returncode

    def close(self):
        """
        Terminate the newly created process
        """
        try:
            self.process.terminate()
            self.return_code = self.process.returncode
        except OSError:
            pass
        self.process.stdin.close()
        self.process.stdout.close()
        self.process.stderr.close()
        self.logger.debug("[{0}] - PJFExecutor successfully completed".format(time.strftime("%H:%M:%S")))

    def init_logger(self):
        """
        Init the default logger
        """
        return PJFLogger.init_logger()
