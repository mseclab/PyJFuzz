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

from wsgiref.simple_server import make_server, WSGIRequestHandler
from bottle import route, run, ServerAdapter, response, request, static_file
from pjf_testcase_server import PJFTestcaseServer
from errors import PJFBaseException
from errors import PJFMissingArgument
from threading import Thread
from pjf_logger import PJFLogger
from pjf_factory import PJFFactory
from certs import CERT_PATH
import multiprocessing
import signal
import time
import ssl
import os
import socket

class WSGIRefServer(ServerAdapter):
    """
    WSGI based server class using SSL
    """
    def run(self, handler):
        class QuietHandler(WSGIRequestHandler):
            def log_request(*args, **kw):
                pass

            def log_error(self, format, *args):
                pass
        self.options['handler_class'] = QuietHandler
        srv = make_server(self.host, self.port, handler, **self.options)
        srv.serve_forever()


class SSLWSGIRefServer(ServerAdapter):
    """
    WSGI based server class using SSL
    """
    def run(self, handler):
        class QuietHandler(WSGIRequestHandler):
            def log_request(*args, **kw):
                pass

            def log_error(self, format, *args):
                pass
        self.options['handler_class'] = QuietHandler
        srv = make_server(self.host, self.port, handler, **self.options)
        srv.socket = ssl.wrap_socket(srv.socket, certfile=CERT_PATH, server_side=True)
        srv.serve_forever()


class PJFServer:
    """
    Class used to run both HTTP and HTTPS server using bottle web server
    """
    def __init__(self, configuration):
        self.client_queue = multiprocessing.Queue(0)
        self.apply_patch()
        self.logger = self.init_logger()
        if ["debug", "html", "content_type", "notify", "ports"] not in configuration:
            raise PJFMissingArgument()
        if configuration.debug:
            print "[\033[92mINFO\033[0m] Starting HTTP ({0}) and HTTPS ({1}) built-in server...".format(
                configuration.ports["servers"]["HTTP_PORT"],
                configuration.ports["servers"]["HTTPS_PORT"]
            )
        if not configuration.content_type:
            configuration.content_type = False
        if not configuration.content_type:
            configuration.content_type = "application/json"
        self.config = configuration
        self.json = PJFFactory(configuration)
        self.https = SSLWSGIRefServer(host="0.0.0.0", port=self.config.ports["servers"]["HTTPS_PORT"])
        self.http = WSGIRefServer(host="0.0.0.0", port=self.config.ports["servers"]["HTTP_PORT"])
        self.httpsd = multiprocessing.Process(target=run, kwargs={"server": self.https, "quiet": True})
        self.httpd = multiprocessing.Process(target=run, kwargs={"server": self.http, "quiet": True})
        if self.config.fuzz_web:
            self.request_checker = Thread(target=self.request_pool, args=())
        self.logger.debug("[{0}] - PJFServer successfully initialized".format(time.strftime("%H:%M:%S")))

    def run(self):
        """
        Start the servers
        """
        route("/")(self.serve)
        if self.config.html:
            route("/<filepath:path>")(self.custom_html)
        if self.config.fuzz_web:
            self.request_checker.start()
        self.httpd.start()
        self.httpsd.start()

    def save_testcase(self, ip, testcases):
        try:
            count = 0
            dir_name = "testcase_{0}".format(ip)
            print "[\033[92mINFO\033[0m] Client {0} seems to not respond anymore, saving testcases".format(ip)
            try:
                os.mkdir(dir_name)
            except OSError:
                pass
            for test in testcases:
                with open("{0}/testcase_{1}.json".format(dir_name, count), "wb") as t:
                    t.write(test)
                    t.close()
                    count += 1
        except Exception as e:
            raise PJFBaseException(e.message)

    def request_pool(self):
        try:
            clients = {}
            end = False
            while not end:
                try:
                    client = self.client_queue.get(timeout=5)
                    if client == (0,0):
                        end = True
                    else:
                        if client[0] not in clients:
                            clients.update({client[0]: {"timestamp": time.time(), "testcases": []}})
                        else:
                            clients[client[0]]["timestamp"] = time.time()
                            if len(clients[client[0]]["testcases"]) <= 10:
                                clients[client[0]]["testcases"].append(client[1])
                            else:
                                clients[client[0]]["testcases"].pop(0)
                                clients[client[0]]["testcases"].append(client[1])
                except:
                    pass
                for c in clients.keys():
                    if time.time() - clients[c]["timestamp"] >= 30:
                        self.save_testcase(c, clients[c]["testcases"])
                        del clients[c]
        except Exception as e:
            raise PJFBaseException(e.message)


    def stop(self):
        """
        Kill the servers
        """
        os.kill(self.httpd.pid, signal.SIGKILL)
        os.kill(self.httpsd.pid, signal.SIGKILL)
        self.client_queue.put((0,0))
        if self.config.fuzz_web:
            self.request_checker.join()
        self.logger.debug("[{0}] - PJFServer successfully completed".format(time.strftime("%H:%M:%S")))

    def custom_html(self, filepath):
        """
        Serve custom HTML page
        """
        try:
            response.headers.append("Access-Control-Allow-Origin", "*")
            response.headers.append("Accept-Encoding", "identity")
            response.headers.append("Content-Type", "text/html")
            return static_file(filepath, root=self.config.html)
        except Exception as e:
            raise PJFBaseException(e.message)

    def serve(self):
        """
        Serve fuzzed JSON object
        """
        try:
            fuzzed = self.json.fuzzed
            if self.config.fuzz_web:
                self.client_queue.put((request.environ.get('REMOTE_ADDR'), fuzzed))
            response.headers.append("Access-Control-Allow-Origin", "*")
            response.headers.append("Accept-Encoding", "identity")
            response.headers.append("Content-Type", self.config.content_type)
            if self.config.notify:
                PJFTestcaseServer.send_testcase(fuzzed, '127.0.0.1', self.config.ports["servers"]["TCASE_PORT"])
            yield fuzzed
        except Exception as e:
            raise PJFBaseException(e.message)

    def init_logger(self):
        """
        Init the default logger
        """
        return PJFLogger.init_logger()

    def apply_patch(self):
        """
        Fix default socket lib to handle client disconnection while receiving data (Broken pipe)
        """
        from patch.socket import socket as patch
        socket.socket = patch
