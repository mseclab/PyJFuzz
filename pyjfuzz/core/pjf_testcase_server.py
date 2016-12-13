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
import time
import threading
import struct
import socket
from pjf_logger import PJFLogger
from errors import PJFMissingArgument, PJFBaseException, PJFSocketError


class PJFTestcaseServer(object):
    def __init__(self, configuration):
        self.logger = self.init_logger()
        if ["ports"] not in configuration:
            raise PJFMissingArgument("PJFTesecaseServer needs \"ports\" argument inside config object")
        self.config = configuration
        self.testcase = []
        self.starting = True
        self.number_of_testcase = 0
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind(('', self.config.ports["servers"]["TCASE_PORT"]))
        self.logger.debug("[{0}] - PJFTestcaseServer successfully initialized".format(time.strftime("%H:%M:%S")))

    def handle(self, sock):
        """
        Handle the actual TCP connection
        """
        try:
            size = struct.unpack("<I", sock.recv(4))[0]
            data = ""
            while len(data) < size:
                data += sock.recv(size - len(data))
            if len(self.testcase) >= 100:
                del self.testcase
                self.testcase = list()
            self.testcase.append(data)
            sock.close()
        except socket.error as e:
            raise PJFSocketError(e.message)
        except Exception as e:
            raise  PJFBaseException(e.message)

    def _shutdown(self, *args):
        """
        Kill TCP server
        """
        self.starting = False
        try:
            self._sock.close()
        except socket.error:
            pass
        self.logger.debug("[{0}] - PJFTestcaseServer successfully completed".format(time.strftime("%H:%M:%S")))

    def increment_testcase(self):
        """
        Increment the testcase number
        """
        self.number_of_testcase += 1

    def got_testcase(self):
        """
        Check if a testcase was received
        """
        return len(self.testcase) > self.number_of_testcase

    def listen(self):
        """
        Listen on host:port
        """
        self._sock.listen(1)
        while self.starting:
            try:
                sock, ip = self._sock.accept()
                threading.Thread(target=self.handle, args=(sock,)).start()
            except socket.error:
                pass

    def start(self):
        """
        Start TCP Server
        """
        self.starting = True
        threading.Thread(target=self.listen).start()

    def init_logger(self):
        """
        Init the default logger
        """
        return PJFLogger.init_logger()

    @staticmethod
    def send_testcase(json, ip, port):
        """
        Send a raw testcase
        """
        try:
            json = struct.pack("<I", len(json)) + json
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((ip, int(port)))
                s.send(json)
                s.shutdown(socket.SHUT_RDWR)
                s.close()
                return True
            except socket.error:
                return False
        except socket.error as e:
            raise PJFSocketError(e.message)
        except Exception as e:
            raise  PJFBaseException(e.message)
