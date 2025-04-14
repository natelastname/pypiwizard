#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2025-02-04T09:23:32-05:00

@author: nate
"""

import argparse
import ast
import asyncio
import atexit
import datetime
import importlib as il
import json
import modulefinder as mf
import os
import pkgutil
import re
import shlex
import subprocess as sp
import sys
from collections import namedtuple

import aiohttp
import feud
import rich_click as click
from dataclass_click import dataclass_click

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
            if not node.module:
                module = "."
            else:
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


def get_abstract(module_path):
    with open(module_path, "r") as file:
        tree = ast.parse(file.read())
    dependencies = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name
        elif isinstance(node, ast.ImportFrom):
            yield node.module
    return


def dotpath_to_file_path(dotpath):
    package_name, *module_names = dotpath.split('.')
    spec = il.util.find_spec(package_name)
    if spec is None:
        return None
    package_dir = os.path.dirname(spec.origin)
    file_path = os.path.join(package_dir, *module_names)
    file_path = file_path.replace('.', os.sep) + '.py'
    return file_path


def is_std_lib(pkg_name):
    if pkg_name in sys.stdlib_module_names:
        return True
    return False



def get_pkg_name(import_name):

    spec = il.util.find_spec(import_name)
    version = il.metadata.version(import_name)

    def get_installable_name(import_package_name):
        distributions = il.metadata.distributions()
        for distribution in distributions:
            p0 = distribution.from_name(import_package_name)
            return p0.name
        return import_package_name

    name0 = get_installable_name(import_name)
    return (name0, version)


@click.command()
@dataclass_click(ppw.types.FindImportsArgs)
def find_abstract_deps(args: ppw.types.FindImportsArgs):
    """Inspect the imports of a python package."""
    if not os.path.exists(args.inpath):
        return 1
    import DictOnly as do
    d0 = do.DictOnly({})
    d0 = {}
    for dotpath, imports in enumerate_modules(args.inpath):
        filepath = dotpath_to_file_path(dotpath)
        for import_name in get_abstract(filepath):
            if is_std_lib(import_name):
                continue
            try:
                name, version = get_pkg_name(import_name)
            except il.metadata.PackageNotFoundError:
                continue

            d0[name] = version

    if not args.flat:
        print(json.dumps(d0, indent=2))
        return

    items = sorted(d0.items(), key= lambda item: item[0])
    for key, val in items:
        print(f'{key} = "^{val}"')

    return


@click.command()
@dataclass_click(ppw.types.FindImportsArgs)
def find_imports(args: ppw.types.FindImportsArgs):
    """Inspect the imports of a python package."""
    if not os.path.exists(args.inpath):
        return 1
    import DictOnly as do
    d0 = do.DictOnly({})
    for dotpath, imports in enumerate_modules(args.inpath):
        print("####################################################")
        print(f"{dotpath}")
        print("####################################################")
        all_imports = []
        for i, item in enumerate(imports):
            print(f"{i:5}: {item}")
            all_imports.append(item)
        d0.set(*dotpath.split('.'), val=all_imports)
    if not args.flat:
        print(json.dumps(d0.tree,indent=2))
    return
