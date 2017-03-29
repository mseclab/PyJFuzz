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
import logging

PYJFUZZ_LOGLEVEL = logging.INFO

PYJFUZZ_COMPANY = 'Mobile Security Lab 2016'

PYJFUZZ_VERSION = '1.1.2'

PYJFUZZ_AUTHOR = "Daniele 'dzonerzy' Linguaglossa"

PYJFUZZ_MAIL = 'd.linguaglossa@mseclab.com'

PYJFUZZ_LOGO = """\033[92mStarting PyJFuzz - {0}\033[95m
  _____            _ ______
 |  __ \          | |  ____|
 | |__) |   _     | | |__ _   _ ________
 |  ___/ | | |_   | |  __| | | |_  /_  /
 | |   | |_| | |__| | |  | |_| |/ / / /
 |_|    \__, |\____/|_|   \__,_/___/___| \033[0m\033[91mv\033[0m{1}\033[95m
         __/ |
        |___/
\033[0m
\033[92mAuthor\033[0m: {2}
\033[92mMail\033[0m: {3}
""".format(PYJFUZZ_COMPANY, PYJFUZZ_VERSION, PYJFUZZ_AUTHOR, PYJFUZZ_MAIL)