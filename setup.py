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
from setuptools import setup
import commands
import os

def get_package_data():
    data = ['core/certs/server.pem', 'core/conf/config.json']
    cur_dir = os.getcwd()
    os.chdir("pyjfuzz")
    data.extend(commands.getoutput("find core/tools -name \"*.*\"").split("\n"))
    os.chdir(cur_dir)
    return data


setup(
    name="PyJFuzz",
    version="1.1.0",
    author="Daniele Lingualossa",
    author_email="d.linguaglossa@mseclab.it",
    description="Trivial JSON fuzzer written in python",
    license="MIT",
    keywords="",
    url="https://github.com/mseclab/PyJFuzz",
    packages=["pyjfuzz",
              "pyjfuzz.core",
              "pyjfuzz.core.errors",
              "pyjfuzz.core.certs",
              "pyjfuzz.core.conf",
              "pyjfuzz.core.tools",
              "pyjfuzz.core.patch"],
    package_data={'pyjfuzz': get_package_data()
                  },
    entry_points={
            'console_scripts': [
                'pjf=pyjfuzz.pyjfuzz:main',
            ],
    },
    install_requires=[
        'bottle',
        'netifaces',
        'GitPython',
        'gramfuzz'
    ],
)

