#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2025-02-04T09:23:32-05:00

@author: nate
"""

import os
import re
import sys
import json
import argparse
import subprocess as sp
import datetime
import atexit
import ast
from collections import namedtuple

import asyncio
import aiohttp
import feud
import shlex

import modulefinder as mf
import importlib as il
import pkgutil
#from modulefinder import ModuleFinder
import pypiwizard as ppw

Import = namedtuple("Import", ["module", "name", "alias"])

logger = ppw.util.get_logger(__name__)

def subproc(cmd):
    shlex.split(cmd)
    result = sp.call(cmd.strip(), shell=True, executable='/bin/bash')
    return result

basedir = os.path.dirname(__file__)
outpath = os.path.join(basedir, "output")
os.makedirs(outpath, exist_ok=True)

# Not used
def import_module(name, package=None):
    """An approximate implementation of import."""
    absolute_name = importlib.util.resolve_name(name, package)
    try:
        return sys.modules[absolute_name]
    except KeyError:
        pass

    path = None
    if '.' in absolute_name:
        parent_name, _, child_name = absolute_name.rpartition('.')
        parent_module = import_module(parent_name)
        path = parent_module.__spec__.submodule_search_locations
    for finder in sys.meta_path:
        spec = finder.find_spec(absolute_name, path)
        if spec is not None:
            break
    else:
        msg = f'No module named {absolute_name!r}'
        raise ModuleNotFoundError(msg, name=absolute_name)
    module = importlib.util.module_from_spec(spec)
    sys.modules[absolute_name] = module
    spec.loader.exec_module(module)
    if path is not None:
        setattr(parent_module, child_name, module)
    return module

def get_imports(path):
    with open(path) as fh:
       root = ast.parse(fh.read(), path)

    for node in ast.iter_child_nodes(root):
        if isinstance(node, ast.Import):
            module = []
        elif isinstance(node, ast.ImportFrom):
            module = node.module.split('.')
        else:
            continue

        for n0 in node.names:
            yield (module, n0.name)
            #yield Import(module, n0.name.split('.'), n0.asname)


def produce_imports(src):
    imports = []
    for item in get_imports(src):
        parent = '.'.join(item[0])
        if parent == "":
            line = f'import {item[1]}'
        else:
            line = f'from {parent} import {item[1]}'
        imports.append(line)

    imports = sorted(list(set(imports)))

    return imports

def enumerate_modules(inpath, prefix=[]):
    for importer, modname, ispkg in pkgutil.walk_packages(path=[inpath]):
        new_prefix = prefix + [modname]
        if ispkg:
            #print("Package: "+modname)
            pkgpath = importer.path
            spec = importer.find_spec(modname)
            locs = spec.submodule_search_locations
            for loc in locs:
                for module in enumerate_modules(loc, prefix=new_prefix):
                    yield module
            continue

        src = importer.find_spec(modname).origin
        imports = produce_imports(src)

        yield (".".join(new_prefix), imports)

class FindImports(feud.Group):
    """List the imports of a python package."""
    def search(inpath: str):
        """Inspect the imports of a python package."""
        if not os.path.exists(inpath):
            return 1

        all_imports = []
        for dotpath, imports in enumerate_modules(inpath):
            print("####################################################")
            print(f"{dotpath}")
            print("####################################################")
            for i, item in enumerate(imports):
                print(f"{i:5}: {item}")

        return

if __name__ == "__main__":
    feud.run(FindImports)
