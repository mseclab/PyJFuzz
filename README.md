
[![LOGO](https://s30.postimg.org/iolw8xqn5/logo.png)](https://s30.postimg.org/iolw8xqn5/logo.png)
=======
**PyJFuzz** is a small, extensible and ready-to-use framework used to **fuzz JSON inputs**, such as mobile endpoint REST API, JSON implementation, Browsers, cli executable and much more.

<table>
    <tr>
        <th>Version</th>
        <td>
           1.1.0
        </td>
    </tr>
    <tr>
        <th>Homepage</th>
        <td><a href="http://www.mseclab.com/">http://www.mseclab.com/</a></td>
    </tr>
        <th>Github</th>
        <td><a href="https://github.com/mseclab/PyJFuzz">https://github.com/mseclab/PyJFuzz</a></td>
     <tr/>
    <tr>
       <th>Author</th>
       <td><a href="http://www.dzonerzy.net">Daniele Linguaglossa</a> (<a href="http://twitter.com/dzonerzy">@dzonerzy</a>)</td>
    </tr>
    <tr>
        <th>License</th>
        <td>MIT - (see LICENSE file)</td>
    </tr>
</table>

Installation
============

**Dependencies**

In order to work PyJFuzz need a single dependency, **bottle**, you can install it from automatic **setup.py** installation.

**Installation**

You can install PyJFuzz with the following command
```{r, engine='bash', count_lines}
git clone https://github.com/mseclab/PyJFuzz.git && cd PyJFuzz && sudo python setup.py install
```

Documentation and Examples
==========================

**CLI tool**

Once installed PyJFuzz will create both a python library and a command-line utility called **pjf** (screenshot below)

[![MENU](https://s17.postimg.org/6gvbyvzpb/cmdline.png)](https://s17.postimg.org/6gvbyvzpb/cmdline.png)

[![PJF](https://s16.postimg.org/rdq1iwwvp/cmdline2.png)](https://s16.postimg.org/rdq1iwwvp/cmdline2.png)

**Library**

PyJFuzz could also work as a library, you can import in your project like following

```python
from pyjfuzz.lib import *
```
**Classes**

The available object/class are the following:

- ***PJFServer*** - User to start and stop built-in HTTP and HTTPS servers
- ***PJFProcessMonitor*** - Used to monitor process crash, it will automatically restart proccess each time it crash
- ***PJFTestcaseServer*** - The testcase server is used in conjunction with PJFProcessMonitor, whenever a process crash the testcase server will register and store the JSON which cause the crash
- ***PJFFactory*** - It's the main object used to do the real fuzz of JSON objects
- ***PJFConfiguration*** - It's the configuration file for each of the available objects
- ***PJFExternalFuzzer*** - Used by PJFactory is a auxiliary class which provide an interface to other command line fuzzer such as *radamsa*
- ***PJFMutation*** - Used by PJFFactory provide all the mutation used during fuzzing session
- ***PJFExecutor*** - Provides an interface to interact with external process

[![CLASSES](https://s4.postimg.org/7picu4y3h/lib.png)](https://s4.postimg.org/7picu4y3h/lib.png)

**Examples**

Below some trivial example of how-to implement PyJFuzz powered program

*simple_fuzzer.py*
```python
from argparse import Namespace
from pyjfuzz.lib import *

config = PJFConfiguration(Namespace(json={"test": ["1", 2, True]}, nologo=True, level=6))
fuzzer = PJFFactory(config)
while True:
    print fuzzer.fuzzed
```

*simple_server.py*
```python
from argparse import Namespace
from pyjfuzz.lib import *

config = PJFConfiguration(Namespace(json={"test": ["1", 2, True]}, nologo=True, level=6, debug=True, indent=True))
PJFServer(config).run()

```

Sometimes you may need to modify standard non customizable settings such as HTTPS or HTTP server port, this can be done in the following way

``` python
from argparse import Namespace
from pyjfuzz.lib import *

config = PJFConfiguration(Namespace(json={"test": ["1", 2, True]}, nologo=True, level=6, indent=True))
print config.ports["servers"]["HTTP_PORT"]   # 8080
print config.ports["servers"]["HTTPS_PORT"]  # 8443
print config.ports["servers"]["TCASE_PORT"]  # 8888
config.ports["servers"]["HTTPS_PORT"] = 443  # Change HTTPS port to 443
```
**Remember**: *When changing default ports, you should always handle exception due to needed privileges!*

Below a comprehensive list of all available settings / customization of PJFConfiguration object:

**Configuration table**

<table>
  <tr>
    <th>Name</th>
    <th>Type</th>
    <th>Description</th>
  </tr>
  <tr>
    <td>json</td>
    <td><b>dict</b></td>
    <td>JSON object to fuzz</td>
  </tr>
  <tr>
    <td>json_file</td>
    <td><b>str</b></td>
    <td>Path to a JSON file</td>
  </tr>
  <tr>
    <td>parameters</td>
    <td><b>list</b>&lt;str&gt;</td>
    <td>List of parameters to fuzz (taken from JSON object)</td>
  </tr>
  <tr>
    <td>techniques</td>
    <td><b>str</b>&lt;int&gt;</td>
    <td>String of enable attacks, used to generate fuzzed JSON, such as XSS, LFI etc. ie "CHPTRSX" (Look <b>techniques table</b>)</td>
  </tr>
  <tr>
    <td>level</td>
    <td><b>int</b></td>
    <td>Fuzzing level in the range 0-6</td>
  </tr>
  <tr>
    <td>utf8</td>
    <td><b>bool</b></td>
    <td>If true switch from unicode encode to pure byte representation</td>
  </tr>
 <tr>
    <td>indent</td>
    <td><b>bool</b></td>
    <td>Set whenever to indent the result object</td>
  </tr>
  <tr>
    <td>url_encode</td>
    <td><b>bool</b></td>
    <td>Set whenever to URLEncode the result object</td>
  </tr>
  <tr>
    <td>strong_fuzz</td>
    <td><b>bool</b></td>
    <td>Set whenever to use <i>strong fuzzing</i> (strong fuzzing will not maintain JSON structure, usefull for parser fuzzing)</td>
  </tr>
  <tr>
    <td>debug</td>
    <td><b>bool</b></td>
    <td>Set whenever to enable debug prints</td>
  </tr>
  <tr>
    <td>exclude</td>
    <td><b>bool</b></td>
    <td>Exclude from fuzzing parameters selected by parameters option</td>
  </tr>
  <tr>
    <td>notify</td>
    <td><b>bool</b></td>
    <td>Set whenever to notify process monitor when a crash occurs only used with PJFServer</td>
  </tr>
  <tr>
    <td>html</td>
    <td><b>str</b></td>
    <td>Path to an HTML directory to serve within PJFServer</td>
  </tr>
  <tr>
    <td>ext_fuzz</td>
    <td><b>bool</b></td>
    <td>Set whenever to use binary from "command" as an externale fuzzer</td>
  </tr>
    <tr>
    <td>cmd_fuzz</td>
    <td><b>bool</b></td>
    <td>Set whenever to use binary from "command" as fuzzer target</td>
  </tr>
    <tr>
    <td>content_type</td>
    <td><b>str</b></td>
    <td>Set the content type result of PJFServer (default <b>application/json</b>)</td>
  </tr>
  <tr>
    <td>command</td>
    <td><b>list</b>&lt;str&gt;</td>
    <td>Command to execute each paramester is a list element, you could use <b>shlex.split</b> from python</td>
  </tr>
</table>

**Techniques table**

<table>
  <tr>
    <th>Index</th>
    <th>Description</th>
  </tr>
  <tr>
    <td>0</td>
    <td>XSS injection (Polyglot)</td>
  </tr>
  <tr>
    <td>1</td>
    <td>SQL injection (Polyglot)</td>
  </tr>
  <tr>
    <td>2</td>
    <td>LFI attack</td>
  </tr>
  <tr>
    <td>3</td>
    <td>SQL injection polyglot (2)</td>
  </tr>
  <tr>
    <td>4</td>
    <td>XSS injection (Polyglot) (2)</td>
  </tr>
  <tr>
    <td>5</td>
    <td>RCE injection (Polyglot)</td>
  </tr>
  <tr>
    <td>6</td>
    <td>LFI attack (2)</td>
  </tr>
  <tr>
    <td>7</td>
    <td>Data URI attack</td>
  </tr>
  <tr>
    <td>8</td>
    <td>LFI and HREF attack</td>
  </tr>
  <tr>
    <td>9</td>
    <td>Header injection</td>
  </tr>
  <tr>
    <td>10</td>
    <td>RCE injection (Polyglot) (2)</td>
  </tr>
  <tr>
    <td>11</td>
    <td>Generic templace injection</td>
  </tr>
  <tr>
    <td>12</td>
    <td>Flask template injection</td>
  </tr>
  <tr>
    <td>13</td>
    <td>Random character attack</td>
  </tr>
</table>

Screenshots
===========

Below some screenshot just to let you know what you should expect from PyJFuzz

[![CLI](https://s18.postimg.org/qu5j9pw09/ext_fuzz.png)](https://s18.postimg.org/qu5j9pw09/ext_fuzz.png)

[![CLI2](https://s11.postimg.org/qtgi9dro3/filefuzz.png)](https://s11.postimg.org/qtgi9dro3/filefuzz.png)

[![CLI3](https://s15.postimg.org/7jn4ktkcb/processm.png)](https://s15.postimg.org/7jn4ktkcb/processm.png)

Built-in tool
===========
PyJFuzz is shipped with a built-in tool called **PyJFuzz Web Fuzzer**, this tool will provide an automatic fuzzing console via HTTP and HTTPS server, it can be used to easly fuzz almost any web browser even when you can't control the process state!

There are two switch used to launch this tool (--browser-auto and --fuzz-web), the first one perform automatic browser restart when a crash occur, the other one try to catch when a browser doesn't make requests anymore. Both of them always save the testcases, below some screenshots.

[![FUZZ](https://s18.postimg.org/ulahts5bt/fuzzweb.png)](https://s18.postimg.org/ulahts5bt/fuzzweb.png)

[![FUZZ2](https://s17.postimg.org/74s3qidrj/fuzzweb2.png)](https://s17.postimg.org/74s3qidrj/fuzzweb2.png)

[![BROWSERAUTO](https://s18.postimg.org/j0t67tabt/auto.png)](https://s18.postimg.org/j0t67tabt/auto.png)

[![BROWSERAUTO2](https://s15.postimg.org/qj2o5it2z/auto2.png)](https://s15.postimg.org/qj2o5it2z/auto2.png)
Issue
=====

Please send any issue here via GitHub I'll provide a fix as soon as possible.

Result
======
*Below a list of know issue found by PyJFuzz, the list will be updated weekly*

- Double free in cJSON (https://github.com/DaveGamble/cJSON/issues/105)
- Unhandled exception in picojson (https://github.com/kazuho/picojson/issues/94)
- Memory leak in simpleJSON (https://github.com/nbsdx/SimpleJSON/issues/8)
- Stack base buffer overflow in frozen (https://github.com/cesanta/frozen/issues/14)
- Memory corruption with custom EIP (https://github.com/cesanta/frozen/issues/15)

End
===

Thanks for using PyJFuzz!

***Happy Fuzzing*** from mseclab
