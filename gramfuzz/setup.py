#!/usr/bin/env python
# encoding: utf-8

import os, sys
from setuptools import setup

setup(
    # metadata
    name             = 'gramfuzz',
    description      = 'gramfuzz is a python-based grammar fuzzer',
    long_description = """
gramfuzz is a python-based grammar fuzzer that is ideally
suited for complex text and binary grammars.

A few of the main features of gramfuzz are:

* dynamic modification of grammars during runtime (and generation!)
* random rule generation
* separate rule definition categories
* probability-based fuzzing/generation
* targeted grammar category fuzzing
* loading grammar files (python) by path
* and more!
""",
    license          = 'MIT',
    version          = '1.2.0',
    author           = 'James \'d0c_s4vage\' Johnson',
    maintainer       = 'James \'d0c_s4vage\' Johnson',
    author_email     = 'd0c.s4vage@gmail.com',
    url              = 'https://github.com/d0c-s4vage/gramfuzz',
    platforms        = 'Cross Platform',
	download_url     = "https://github.com/d0c-s4vage/gramfuzz/tarball/v1.2.0",
    classifiers      =  [
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    packages= ['gramfuzz'],
)
