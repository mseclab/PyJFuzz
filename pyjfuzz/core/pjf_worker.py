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
from errors import PJFBaseException
from pjf_updater import PJFUpdater
from pjf_configuration import PJFConfiguration
from pjf_server import PJFServer
from pjf_factory import PJFFactory
from pjf_process_monitor import PJFProcessMonitor
from pjf_external_fuzzer import PJFExternalFuzzer
from errors import PJFMalformedJSON
from argparse import Namespace
import tempfile
import json as json_eval
import netifaces
import time
import sys
import os

class PJFWorker(object):

    def __init__(self, config):
        self.config = config

    def browser_autopwn(self):
        try:
            from tools import TOOLS_DIR
            if not self.config.auto:
                to_fuzz = {'lvl1': {"lvl2": [1, 1.0, "True"]}, "lvl1-1": [{"none": None, "inf": [{"a": {"a": "a"}}]}]}
            else:
                to_fuzz = self.config.generate_json(self.config.grammar_path)
            run = "{0} http://127.0.0.1:8080/fuzzer.html".format(self.config.browser_auto)
            config = PJFConfiguration(Namespace(json=to_fuzz,
                                                html=TOOLS_DIR,
                                                ports=self.config.ports,
                                                content_type="text/plain",
                                                debug=True,
                                                nologo=True,
                                                level=2,
                                                utf8=self.config.utf8,
                                                indent=self.config.indent,
                                                notify=True,
                                                strong_fuzz=self.config.strong_fuzz,
                                                process_to_monitor=run,
                                                recheck_ports=False))
            monitor = PJFProcessMonitor(config)
            server = PJFServer(config)
            server.run()
            try:
                while True:
                        monitor.start_monitor(standalone=False)
            except KeyboardInterrupt:
                monitor.shutdown()
                server.stop()
        except Exception as e:
            raise PJFBaseException(e.message)

    def web_fuzzer(self):
        try:
            from tools import TOOLS_DIR
            if not self.config.auto:
                to_fuzz = {'lvl1': {"lvl2": [1, 1.0, "True"]}, "lvl1-1": [{"none": None, "inf": [{"a": {"a": "a"}}]}]}
            else:
                to_fuzz = self.config.generate_json(self.config.grammar_path)
            run = "{0} http://127.0.0.1:8080/fuzzer.html".format(self.config.browser_auto)
            config = PJFConfiguration(Namespace(json=to_fuzz,
                                                html=TOOLS_DIR,
                                                ports=self.config.ports,
                                                content_type="text/plain",
                                                debug=True,
                                                nologo=True,
                                                level=2,
                                                utf8=self.config.utf8,
                                                indent=self.config.indent,
                                                notify=True,
                                                fuzz_web=True,
                                                strong_fuzz=self.config.strong_fuzz,
                                                process_to_monitor=run,
                                                recheck_ports=False))
            server = PJFServer(config)
            server.run()
            print "[\033[92mINFO\033[0m] Available URLs"
            for url in self.get_urls():
                print "[\033[92m*\033[0m] {0}".format(url)
            try:
                while True:
                        time.sleep(1)
            except KeyboardInterrupt:
                server.stop()
        except Exception as e:
            raise PJFBaseException(e.message)

    def get_urls(self):
        try:
            for iface in netifaces.interfaces():
                net = netifaces.ifaddresses(iface)
                if netifaces.AF_INET in net:
                    yield "http://{0}:{1}/fuzzer.html".format(net[netifaces.AF_INET][0]['addr'],
                                                              self.config.ports["servers"]["HTTP_PORT"])
        except Exception as e:
            raise PJFBaseException(e.message)

    def start_process_monitor(self):
        try:
            PJFProcessMonitor(self.config).start_monitor()
        except Exception as e:
            raise PJFBaseException(e.message)

    def start_file_fuzz(self):
            with open(self.config.json_file, "rb") as json_file:
                j = json_file.read()
                json = None
                try:
                    if not self.config.strong_fuzz:
                        setattr(self.config, "json", json_eval.loads(j))
                        json = PJFFactory(self.config)
                    else:
                        setattr(self.config, "json", json_eval.loads(j))
                        json = PJFFactory(self.config)
                except:
                    raise PJFMalformedJSON()
                json_file.close()
            if json:
                with open(self.config.json_file, "wb") as json_file:
                    json_file.write(json.fuzzed)

    def start_http_server(self):
        try:
            server = PJFServer(self.config)
            server.run()
            try:
                while True:
                        time.sleep(1)
            except KeyboardInterrupt:
                server.stop()
        except Exception as e:
            raise PJFBaseException(e.message)

    def fuzz_command_line(self):
        try:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(json_eval.dumps(self.config.json))
                temp_file.close()
                setattr(self, "temp_file_name", temp_file.name)
                if self.config.debug:
                    print "[\033[92mINFO\033[0m] Generated temp file \033[91m%s\033[0m" % self.config.temp_file_name
            result = PJFExternalFuzzer(self.config).execute(self.config.temp_file_name)
            with open(self.config.temp_file_name, "wb") as fuzzed:
                fuzzed.write(result)
                fuzzed.close()
        except Exception as e:
            raise PJFBaseException(e.message)

    def fuzz_stdin(self):
        try:
            result = PJFExternalFuzzer(self.config).execute(json_eval.dumps(self.config.json))
            if result:
                sys.stdout.write(result)
            else:
                self.fuzz()
        except Exception as e:
            raise PJFBaseException(e.message)

    def fuzz_external(self, stdin_input=False):
        try:
            import shlex
            import os
            dir_name = "testcase_{0}".format(os.path.basename(shlex.split(self.config.command[0])[0]))
            try:
                f = [0]
                for (_, _, filenames) in os.walk(dir_name):
                    f.extend([int(t.split("_")[1].split(".")[0]) for t in filenames])
                    break
                last = max(f) + 1
            except OSError:
                last = 0
            j = PJFFactory(self.config)
            j_fuzz = j.fuzzed
            if not stdin_input:
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    temp_file.write(j_fuzz)
                    temp_file.close()
                    setattr(self.config, "temp_file_name", temp_file.name)
                if self.config.debug:
                    print "[\033[92mINFO\033[0m] Generated temp file \033[91m%s\033[0m" % self.config.temp_file_name
                result = PJFExternalFuzzer(self.config).execute_sigsegv(self.config.temp_file_name)
            else:
                setattr(self.config, "temp_file_name", False)
                result = PJFExternalFuzzer(self.config).execute_sigsegv(j_fuzz)
            if result:
                print "[\033[92mINFO\033[0m] Program crashed with \033[91mSIGSEGV\033[0m/\033[91mSIGABRT\033[0m/\033[91mSIGHUP\033[0m"
                if self.config.debug:
                    print "[\033[92mINFO\033[0m] Saving testcase..."
                try:
                    os.mkdir(dir_name)
                except OSError:
                    pass
                with open("{0}/testcase_{1}.json".format(dir_name, last), "wb") as t:
                    t.write(j_fuzz)
                    t.close()
            else:
                if self.config.temp_file_name:
                    os.unlink(self.config.temp_file_name)
                print "[\033[92mINFO\033[0m] Program exited normally"
        except Exception as e:
            raise PJFBaseException(e.message)

    def fuzz(self):
        try:
            json = PJFFactory(self.config)
            sys.stdout.write("{0}\n".format(json.fuzzed))
        except Exception as e:
            raise PJFBaseException(e.message)

    def update_library(self):
        if os.getuid() != 0:
            print "[\033[92mINFO\033[0m] You need to run as root!"
        else:
            updater = PJFUpdater()
            updater.update()