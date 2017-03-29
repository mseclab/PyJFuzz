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
from gramfuzz.fields import *
import gramfuzz

def generate_json(path):
    grammar = gramfuzz.GramFuzzer()
    grammar.load_grammar(path)
    for x in grammar.gen(cat="json", num=10, max_recursion=10):
        if x not in ["{}", "[]"]:
            j = json.loads(x)
            del grammar
            return j
    return {"dummy": 1}

TOP_CAT = "json"

class RDef(Def): cat="json-def"

class RRef(Ref): cat="json-def"

Def("json",
    RRef("json-object") | RRef("json-array"),
cat="json")

RDef("json-array",
     And("[",Join(RRef("value"), max=3, sep=","), "]") |
     And('[',Join(RRef("empty"), max=1), "]") |
     And('[',Join(RRef("json-array"), max=3, sep=","), "]")|
     And('[',Join(RRef("json-object"), max=3, sep=","), "]")
)

RDef("key-value",

     RRef("key") & ":" & RRef("value")

)

RDef("key-array",

     RRef("key") & ":" & RRef("json-array")

)

RDef("key-object",

     RRef("key") & ":" & RRef("json-object")

)

RDef("json-object",
     And("{", Join(RRef("key-value"), max=3, sep=","), "}") |
     And("{", Join(RRef("key-array"), max=3, sep=","), "}") |
     And("{", Join(RRef("key-object"), max=3, sep=","), "}") |
     And("{", RRef("empty"), "}")

)

RDef("key",
     Q(String(charset=String.charset_alphanum, min=5, max=10))
)

RDef("sep",
    ":"
)

RDef("value",
    Int | Float | RRef("boolean") | RRef("key") | UInt | UFloat | RRef("null")
)

RDef("empty",

     ""
)

RDef("null",
     "null"
)

RDef("boolean",
     Or("true", "false")
)