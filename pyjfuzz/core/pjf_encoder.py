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
from string import printable as p
import json
import sys
import re

class PJFEncoder(object):
    """
    Class that represent a JSON encoder / decoder
    """

    @staticmethod
    def json_encode(func):
        """
        Decorator used to change the return value from PJFFactory.fuzzed, it makes the structure printable
        """
        def func_wrapper(self, indent, utf8):
            if utf8:
                encoding = "\\x%02x"
            else:
                encoding = "\\u%04x"
            hex_regex = re.compile(r"(\\\\x[a-fA-F0-9]{2})")
            unicode_regex = re.compile(r"(\\u[a-fA-F0-9]{4})")

            def encode_decode_all(d, _decode=True):
                if type(d) == dict:
                    for k in d:
                        if type(d[k]) in [dict, list]:
                            if _decode:
                                d[k] = encode_decode_all(d[k])
                            else:
                                d[k] = encode_decode_all(d[k], _decode=False)
                        elif type(d[k]) == str:
                            if _decode:
                                d[k] = decode(d[k])
                            else:
                                d[k] = encode(d[k])
                elif type(d) == list:
                    arr = []
                    for e in d:
                        if type(e) == str:
                            if _decode:
                                arr.append(decode(e))
                            else:
                                arr.append(encode(e))
                        elif type(e) in [dict, list]:
                            if _decode:
                                arr.append(encode_decode_all(e))
                            else:
                                arr.append(encode_decode_all(e, _decode=False))
                        else:
                            arr.append(e)
                    return arr
                else:
                    if _decode:
                        return decode(d)
                    else:
                        return encode(d)
                return d

            def decode(x):
                tmp = "".join(encoding % ord(c) if c not in p else c for c in x)
                if sys.version_info >= (3, 0):
                    return str(tmp)
                else:
                    for encoded in unicode_regex.findall(tmp):
                        tmp = tmp.replace(encoded, encoded.decode("unicode_escape"))
                    return unicode(tmp)

            def encode(x):
                for encoded in hex_regex.findall(x):
                    if sys.version_info >= (3, 0):
                        x = x.replace(encoded, bytes(str(encoded).replace("\\\\x", "\\x"),"utf-8").decode("unicode_escape"))
                    else:
                        x = x.replace(encoded, str(encoded).replace("\\\\x", "\\x").decode("string_escape"))
                return x

            if indent:
                return encode_decode_all("{0}".format(json.dumps(encode_decode_all(func(self)), indent=5)),
                                         _decode=False)
            else:
                return encode_decode_all("{0}".format(json.dumps(encode_decode_all(func(self)))), _decode=False)

        return func_wrapper
