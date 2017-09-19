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
import time
import subprocess
import signal
import shlex
from subprocess import PIPE
from .pjf_executor import PJFExecutor
from .pjf_testcase_server import PJFTestcaseServer
from .errors import PJFMissingArgument ,PJFBaseException, PJFProcessExecutionError

class PJFProcessMonitor(PJFTestcaseServer, PJFExecutor):
    """ Represent a class used to start and monitor a single process """

    def __init__(self, configuration):
        """
        Init the ProcessMonitor server
        """
        self.logger = self.init_logger()
        if ["debug", "ports", "process_to_monitor"] not in configuration:
            raise PJFMissingArgument()
        self.config = configuration
        self.process = None
        self.finished = False
        self.testcase_count = 0
        if self.config.debug:
            print("[\033[92mINFO\033[0m] Starting process monitoring...")
            print("[\033[92mINFO\033[0m] Starting Testcase Server ({0})...".format(
                self.config.ports["servers"]["TCASE_PORT"]
            ))
        super(PJFProcessMonitor, self).__init__(configuration)
        self.logger.debug("[{0}] - PJFProcessMonitor successfully completed".format(time.strftime("%H:%M:%S")))

    def shutdown(self, *args):
        """
        Shutdown the running process and the monitor
        """
        try:
            self._shutdown()
            if self.process:
                self.process.wait()
                self.process.stdout.close()
                self.process.stdin.close()
                self.process.stderr.close()
            self.finished = True
            self.send_testcase('', '127.0.0.1', self.config.ports["servers"]["TCASE_PORT"])
            self.logger.debug("[{0}] - PJFProcessMonitor successfully completed".format(time.strftime("%H:%M:%S")))
        except Exception as e:
            raise PJFBaseException(e.message if hasattr(e, "message") else str(e))

    def save_testcase(self, testcase):
        """
        Save all testcases collected during monitoring
        """
        try:
            if self.config.debug:
                print("[\033[92mINFO\033[0m] Saving testcase...")
            dir_name = "testcase_{0}".format(os.path.basename(shlex.split(self.config.process_to_monitor)[0]))
            try:
                os.mkdir(dir_name)
            except OSError:
                pass
            for test in testcase:
                with open("{0}/testcase_{1}.json".format(dir_name, self.testcase_count), "wb") as t:
                    t.write(test)
                    t.close()
                self.testcase_count += 1
        except Exception as e:
            raise PJFBaseException(e.message if hasattr(e, "message") else str(e))

    def run_and_monitor(self):
        """
        Run command once and check exit code
        """
        signal.signal(signal.SIGINT, self.shutdown)
        self.spawn(self.config.process_to_monitor, timeout=0)
        return self._is_sigsegv(self.return_code)

    def start_monitor(self, standalone=True):
        """
        Run command in a loop and check exit status plus restart process when needed
        """
        try:
            self.start()
            cmdline = shlex.split(self.config.process_to_monitor)
            if standalone:
                signal.signal(signal.SIGINT, self.shutdown)
            self.process = subprocess.Popen(cmdline, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            while self.process and not self.finished:
                self.process.wait()
                if self._is_sigsegv(self.process.returncode):
                    if self.config.debug:
                        print("[\033[92mINFO\033[0m] Process crashed with \033[91mSIGSEGV\033[0m, waiting for testcase...")
                    while not self.got_testcase():
                        time.sleep(1)
                    self.save_testcase(self.testcase[-10:])  # just take last 10 testcases
                if self.process:
                    self.process = subprocess.Popen(cmdline, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        except OSError:
            self.shutdown()
            self.process = False
            self.got_testcase = lambda: True
            raise PJFProcessExecutionError("Binary <%s> does not exist" % cmdline[0])
        except Exception as e:
            raise PJFBaseException("Unknown error please send log to author")

    def _is_sigsegv(self, return_code):
        """
        Check return code against SIGSEGV
        """
        if return_code == -signal.SIGSEGV:
            return True
        return False
