#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2025-03-21T19:28:28-04:00

@author: nate
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import rich_click as click
from dataclass_click import (argument, dataclass_click, option,
                             register_type_inference)
from pydantic import BaseModel


@dataclass
class DlSimpleArgs:
    regex: Annotated[str, option()]
    update_index: Annotated[bool, option(default=False)]
    download: Annotated[bool, option(default=False)]

@dataclass
class SearchArgs:
    regex: Annotated[str, option()]
    update_index: Annotated[bool, option(default=False)]

@dataclass
class FindImportsArgs:
    inpath: Annotated[Path, option()]
    flat: Annotated[bool, option(default=True)]
