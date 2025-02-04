# pypiwizard

`pypiwizard` is a tool for downloading and extracting source distributions (_sdists_) from PyPi for informational / educational purposes.

# Use cases

- Inspecting the source code of packages whose source repository is no longer available.
- Assessing the quality of multiple packages or comparing implementations.
- Auditing the implementations of untrusted or undocumented packages from PyPi.
- Performing programmatic analysis of public packages.

Note that `pypiwizard` never installs any of the packages that it downloads. 

# Features

- `simpledl`
  - Search for packages by Regex
  - Download and extract sdists to `$HOME/pypiwizard_sdists`
- `findimports`
  - Enumerates the modules/packages of an extracted Python package and lists the imported modules.

# Example 1: `findimports`

```
(base) nate@nate-Kudu:~/pypiwizard$ pypiwizard findimports search ./
####################################################
find_imports
####################################################
    0: from collections import namedtuple
    1: import aiohttp
    2: import argparse
    3: import ast
    4: import asyncio
    5: import atexit
    6: import datetime
    7: import feud
    8: import importlib
    9: import json
   10: import modulefinder
   11: import nate_lib
   12: import os
   13: import pkgutil
   14: import re
   15: import shlex
   16: import subprocess
   17: import sys
####################################################
run0
####################################################
    0: import aiohttp
    1: import asyncio
    2: import atexit
    3: import datetime
    4: import feud
    5: import json
    6: import nate_lib
    7: import os
    8: import pypiwizard
    9: import re
   10: import shlex
   11: import subprocess
   12: import sys
####################################################
simple_dl
####################################################
    0: import aiohttp
    1: import argparse
    2: import asyncio
    3: import atexit
    4: import datetime
    5: import feud
    6: import json
    7: import nate_lib
    8: import os
    9: import re
   10: import shlex
   11: import subprocess
   12: import sys

```

# Design considerations

- Uses the package [feud](https://github.com/eonu/feud "feud") for argument parsing
- Uses the package [dtrx](https://github.com/dtrx-py/dtrx "dtrx") for extraction


