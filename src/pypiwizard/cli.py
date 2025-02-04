#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2025-02-04T09:29:07-05:00

@author: nate
"""
import feud

import pypiwizard as ppw

class PypiWizard(feud.Group):
    """Download and inspect sdists of public packages from PyPi."""
    pass

def cli_main():
    PypiWizard.register(ppw.find_imports.FindImports)
    PypiWizard.register(ppw.pypi_dl.SimpleDl)
    feud.run(PypiWizard)
