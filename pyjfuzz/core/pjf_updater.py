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
from pjf_version import PYJFUZZ_VERSION
from distutils.version import StrictVersion
from git import Repo
import subprocess
import tempfile
import urlparse
import httplib
import shutil
import os

class PJFUpdater:

    def __init__(self):
        self.url = "https://github.com/mseclab/PyJFuzz"
        self.tmp_dir = tempfile.mkdtemp()
        self.version_host = "raw.githubusercontent.com"
        self.version_url = "/mseclab/PyJFuzz/master/VERSION"
        self.new_version = ""

    def need_update(self):
        if "HTTP_PROXY" in os.environ or "HTTPS_PROXY" in os.environ:
            if "HTTP_PROXY" in os.environ:
                proxy = urlparse.urlparse(os.environ["HTTP_PROXY"])
            else:
                proxy = urlparse.urlparse(os.environ["HTTPS_PROXY"])
            conn = httplib.HTTPSConnection(proxy.hostname, proxy.port)
            conn.set_tunnel(self.version_host, 443)
        else:
            conn = httplib.HTTPSConnection("raw.githubusercontent.com")
        conn.request("GET", self.version_url)
        version = conn.getresponse().read()
        try:
            if StrictVersion(version) > StrictVersion(PYJFUZZ_VERSION):
                self.new_version = version
                return True
        except:
            pass
        return False

    def install(self, version):
        subprocess.Popen(["python", "{0}/setup.py".format(self.tmp_dir), "install"]).wait()
        proc = subprocess.Popen(["python","-c","from pyjfuzz.lib import PYJFUZZ_VERSION; print PYJFUZZ_VERSION,"],
                                stdout=subprocess.PIPE)
        proc.wait()
        v = proc.stdout.read().replace("\n", "")
        if version == v:
            print "[\033[92mINFO\033[0m] Installation completed!"
            return True
        else:
            print "[\033[92mINFO\033[0m] Something goes wrong please install manually :("
            return False

    def update(self):
        if self.need_update():
            print "[\033[92mINFO\033[0m] Found an updated version! cloning..."

            Repo.clone_from(self.url, self.tmp_dir)
            os.chdir(self.tmp_dir)
            print "[\033[92mINFO\033[0m] Installing..."
            if self.install(self.new_version):
                os.chdir("..")
                shutil.rmtree(self.tmp_dir)
                return True
        else:
            print "[\033[92mINFO\033[0m] You've got already the last version :)"
        shutil.rmtree(self.tmp_dir)
        return False

