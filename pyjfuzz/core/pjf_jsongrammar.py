from gramfuzz.fields import  *

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
    Int() | Float() | RRef("boolean") | RRef("key") | UInt() | UFloat() | RRef("null")
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