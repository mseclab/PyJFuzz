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
from core.pjf_logger import PJFLogger
from core import pjf_configuration
import argparse
import time

def init_logger():
    return PJFLogger.init_logger()

def main():
    logger = init_logger()

    logger.debug("[{0}] - PyJFuzz successfully initialized".format(time.strftime("%H:%M:%S")))

    parser = argparse.ArgumentParser(description='PyJFuzz JSON Fuzzer (c) Mobile Security Lab - 2016',
                                     formatter_class=argparse.RawTextHelpFormatter)

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument('--update', action='store_true', help='Check for updates, and automatically install them',
                       default=False, required=False, dest="update_pjf")

    group.add_argument('--P',  metavar='PROCESS', help='Monitor process for crash', default=False, required=False,
                       dest="process_to_monitor")
    group.add_argument('--J', metavar='JSON', help='Original JSON serialized object',
                       type=pjf_configuration.PJFConfiguration.valid_json, default=None, dest="json")
    group.add_argument('--F', metavar='FILE', help='Path to file', type=pjf_configuration.PJFConfiguration.valid_file,
                       default=None, dest="json_file")

    group.add_argument('--auto', action='store_true', help='Automatically generate JSON init testcase', dest='auto',
                        default=False)

    parser.add_argument('-p', metavar='PARAMS', help='Parameters comma separated', required=False, dest="parameters")

    parser.add_argument('-t', metavar='TECHNIQUES', help='Techniques "CHPTRSX"\n\n'
                                                         'C - Command Execution\n'
                                                         'H - Header Injection\n'
                                                         'P - Path Traversal\n'
                                                         'T - Template Injection\n'
                                                         'R - Random Characters\n'
                                                         'S - SQL Injection\n'
                                                         'X - XSS\n\n', required=False, dest="techniques")
    parser.add_argument('--utf8', action='store_true', help='Enable utf8 invalid bytes', default=False, required=False,
                        dest="utf8")

    parser.add_argument('--content-type', metavar='CONTENT TYPE', help='Set the content type used inside built-in '
                                                                       'servers', default=False, required=False,
                        dest="content_type")

    parser.add_argument('-l', metavar='FUZZ LEVEL', help='Fuzz level [0-6]', type=int, default=6, required=False,
                        dest="level")

    parser.add_argument('-i', action='store_true', help='JSON indent', default=False, required=False,
                        dest="indent")

    parser.add_argument('-ue', action='store_true', help='URLEncode result', default=False, required=False,
                        dest="url_encode")

    parser.add_argument('-d', action='store_true', help='Enable Debug', dest='debug', default=False, required=False)

    parser.add_argument('-s', action='store_true', help='Strong fuzz without maintaining structure', dest='strong_fuzz',
                        default=False, required=False)

    parser.add_argument('-x', action='store_true', help='Exclude params selected by -p switch',
                        dest='exclude_parameters', default=False, required=False)

    parser.add_argument('-ws', action='store_true', help='Enable built-in REST API server', dest='web_server',
                        default=False, required=False)

    parser.add_argument('-n', action='store_true', help='Notify process monitor when a crash occur', dest='notify',
                        default=False, required=False)

    parser.add_argument('-html', metavar='HTLM PATH', help='Path to an HTML file to serve', dest='html',
                        type=pjf_configuration.PJFConfiguration.valid_dir, required=False)

    parser.add_argument('-e', action='store_true', help='Execute the command specified by positional args to fuzz the'
                                                        ' JSON object, use @@ to indicate filename', dest='ext_fuzz',
                        default=False, required=False)

    parser.add_argument('-c', action='store_true', help='Fuzz the command specified by position args, use the payload'
                                                        ' from --J switch, use @@ to indicate filename',
                        dest='cmd_fuzz', default=False, required=False)

    parser.add_argument('--no-logo', action='store_true', help='Disable logo printing at startup', dest='nologo',
                        default=False)

    group.add_argument('--browser-auto', metavar='PATH', help='\033[91mLaunch automatic browser fuzzing session,'
                                                              ' PATH must be the path to browser binary\033[0m',
                       dest='browser_auto', default=False)

    group.add_argument('--fuzz-web', action='store_true', help='\033[91mLaunch automatic web fuzzing session\033[0m',
                       dest='fuzz_web', default=False)

    parser.add_argument('command', nargs='*', help='Command to execute')

    pjf_configuration.PJFConfiguration(parser.parse_args()).start()

    logger.debug("[{0}] - PyJFuzz successfully completed".format(time.strftime("%H:%M:%S")))

if __name__ == "__main__":
    main()
