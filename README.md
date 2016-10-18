# PyJFuzz
PyJFuzz is a trivial and easy-to-use command line python json object fuzzer based on radamsa, it's a random object generator based on the provided object.
It allows both object based and array based fuzzing, the techniques used are:
 - Integer fuzzing using MAX_INT MIN_INT and type changing
 - Boolean fuzzing using string and integer representation
 - String fuzzing using radamsa
 - Object and array fuzzing using above techniques recursively

PyJFuzz simplify the task to fuzz rest API web server since it's a commandline utility and support native urlencode in order to be included inside webapp requests.
## Dependencies
- **Radamsa**

## Usage

```
usage: pyjfuzz.py [-h] -j JSON [-f FUZZ_FACTOR] [-i INDENT] [-ue]

Trivial Python JSON Fuzzer (c) DZONERZY

optional arguments:
  -h, --help      show this help message and exit
  -j JSON         Original JSON serialized object
  -f FUZZ_FACTOR  Fuzz factor [0-6]
  -i INDENT       JSON indent number
  -ue             URLEncode result
```
## Examples

### Simple object fuzzing
```
dzonerzy:jsonfuzz dzonerzy$ python pyjfuzz.py -j '{"element": "fuzzed", "element2": 1}' -i 3
{
   "element2": 4278190081,
   "element": "|u|u|u|fuzzed|u|fuzzed|uzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzedzzed\x0a|fuzzzzzzzzzzzzzed\x0a|fuzz\x0a|fuzz\x0a|fuzz\x0a|fuzz\x0a|fuzz\x0a|fuzz\x0a|fuzz\x0a|fuzz\x0a|fuzz\x0a|fuzz\x0a|fuzz\x0a|fuzz\x0a|fuzz\x0a|fuzz\x0a|fuzz\x0a|fuzz\x0a|fuzz\x0a|fuzz\x0a|fuzz\x0a|fuzzed\x0a"
}
```
```
dzonerzy:jsonfuzz dzonerzy$ python pyjfuzz.py -j '{"element": "fuzzed", "element2": 1}' -i 3
{
   "element2": 287531397,
   "element": [
      "fuzzed"
   ]
}
```
```
dzonerzy:jsonfuzz dzonerzy$ python pyjfuzz.py -j '{"element": "fuzzed", "element2": 1}' -i 3
{
   "element2": 4278190081,
   "element": {
      "param": "'or'=\"'1--fuzzed%0A"
   }
}
```
### Simple array fuzzing
```
dzonerzy:jsonfuzz dzonerzy$ python pyjfuzz.py -j '["pippo","pluto",1,null]' -i 3
[
   false,
   {
      "param": "'or'0\"or'=\"'1\"'or'1\"'1--po%250A'or'1\"or'=\"'1--pluto%250A"
   },
   1,
   null,
   "||calc.exe;&&&id|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3|3\x0a"
]
```
```
dzonerzy:jsonfuzz dzonerzy$ python pyjfuzz.py -j '["pippo","pluto",1,null]' -i 3
[
   "pippo",
   null,
   1,
   null,
   [
      "\\x00",
      "\\x00",
      "\\x00",
      "\\x00"
   ]
]
```
```
dzonerzy:jsonfuzz dzonerzy$ python pyjfuzz.py -j '["pippo","pluto",1,null]' -i 3
[
   "/../../../../etc/passwdpippo%C0%8A",
   "pluto",
   4278190081,
   null
]
```
## URLEncoded payload
PyJFuzz will provide the **-ue** switch which will automatically encode the payload in order to be used via web proxy such as Burp Suite.

```
dzonerzy:jsonfuzz dzonerzy$ python pyjfuzz.py -j '["pippo","pluto",1,null]' -ue
%5B%22pippo%22%2C%20%22pluto%22%2C%201%2C%20%5B%22None%22%5D%5D
```
## Fuzz factor
Fuzz factor allows to generate complex or trivial payload during fuzzing process, you can specify a value from **0** (trivial) to **6** (complex).

### Trivial
```
dzonerzy:jsonfuzz dzonerzy$ python pyjfuzz.py -j '{"a": 1, "b": "2"}' -f 0 -i 3
{
   "a": 255,
   "b": "javascript:alert(/);//2&#x0a;"
}
```
### Complex
```
dzonerzy:jsonfuzz dzonerzy$ python pyjfuzz.py -j '{"a": 1, "b": "2"}' -f 6 -i 3
{
   "a": -1,
   "b": {
      "param": "||calc.exe;&&id|1\\x0a||calc.exe;&&id|1\\x0a||calc.exexe;&&id|1\\x0a||calcalc.exe;&&id|2\\x0a||calc.exe;&&id|1\\x0a||calc.exe;&&id|1\\x0a|{calc.exe;&&id|2\\x0a"
   }
}
```
## Using as a module
PyJFuzz can be install as a standalone module this will provide you the ability to create your custom program based on PyJFuzz!
Below an example:
```python
from pyjfuzz import JSONFactory
import json

fuzzer = JSONFactory()
for _ in range(0, 10):
    fuzzer.initWithJSON(json.dumps({"test": "test", "num": 123, "array": ["hello", 1, True]}))
    fuzzer.ffactor(6)
    print fuzzer.fuzz()
```
The result should be something similiar

```
dzonerzy:jsonfuzz dzonerzy$ python pyjfuzz_as_a_module.py
[INFO] Using (Radamsa 0.3)

{"test":"&#4;------<iies&#243;----<iies&#243;&#160;t&#10;","array":["hello",true,true],"num":123}
{"test":"CCC&#192;&#186;t&#200;].\\&#197;test&#10;","array":[{"param":"sccript"},0,true],"num":-258252615}
{"test":{"param":"0sdtet%0B"},"array":["&#10;","True",true],"num":-291530801}
{"test":"test","array":["hello",-1,"True"],"num":255}
{"test":false,"array":["--><img src=0>-><img src=0>-><img src=0>-><img src=0>-><img src=0>-><img src=0>-><img src=0>-><img src=0>-><img src=0>-><img src=0>-><img src=0>-><img src=0>-><img src=0>-><img src=0>-><img src=0>-><img src=0>-><img src=0>-><img src=0>-><img src=0>-><img src=0>-><img src=0>-><img src=0>-><img src=0>-><img src=0>hello&#x0a;","False",true],"num":123}
{"test":{"param":"C:\\..\\te&#xe1;&#x85;&#x9f;st&#x0a;C:\\..\\te&#xe1;&#x85;&#x9f;st&#x0a;C:\\..\\te&#xe1;&#x85;&#x9f;st&#x0a;"},"array":[".\\hello\u000a;.\\hello\u000a;","True",true],"num":255}
{"test":["test"],"array":[false,-1,true],"num":255}
{"test":"test","array":["hello","True",true],"num":true}
{"test":["test"],"array":[{"param":"./helllo%250A"},1,true],"num":-123}
{"test":{"param":"\"><im'\"><img smg sr'\"><img src=0>tesr'<img src=0>testest\u000a;'\"><img src=0>test\u000a;"},"array":["|$|AAA||${AAAA|$|AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}||$|AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${A|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${ABAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|$|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}|${AAA}}{${ABAA}}h}hello\u000a;{${AAA}}hello\u000a;",1867360077,true],"num":true}
```
## Bonus!
This is a small gift for lazy people, below you will find a link to burp-pyjfuzz a Burp Suite plugin which will implement PyJFuzz for fuzzing purpose!

[Burp-PyJFuzz](https://github.com/dzonerzy/Burp-PyJFuzz)
![Burp](https://s15.postimg.org/574yb5c7f/Schermata_2016_10_18_alle_10_39_18.png "Burp Suite Intruder")
#### End
As i said before this is a dumb fuzzer anyway you can extend in order to fit your needs, please just remember to mention my name.

\#dzonerzy
