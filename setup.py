#!/usr/bin/env python
import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
        name="PyJFuzz",
        version="0.1",
        author="Daniele Lingualossa",
        author_email="danielelinguaglossa@gmail.com",
        description="Trivial JSON fuzzer written in python (based on radamsa)",
        license="MIT",
        keywords="",
        url="https://github.com/dzonerzy/PyJFuzz",
        py_modules=["pyjfuzz"],
        scripts=["pyjfuzz.py"],
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Topic :: Utilities"
        ],
)
