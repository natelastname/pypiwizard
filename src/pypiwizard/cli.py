#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2025-02-04T09:29:07-05:00

@author: nate
"""
import rich_click as click
from dataclass_click import (argument, dataclass_click, option,
                             register_type_inference)
from ebook_to_audio.types import RunArgs, SplitArgs, TOCStrat

import pypiwizard as ppw


@click.group()
def cli():
    """Download and inspect sdists of public packages from PyPi."""
    pass

def cli_main():
    #PypiWizard.register(ppw.find_imports.FindImports)
    #PypiWizard.register(ppw.pypi_dl.SimpleDl)
    #PypiWizard.register(ppw.pypi_dl.search)

    cli.add_command(ppw.find_imports.find_imports)
    cli.add_command(ppw.find_imports.find_abstract_deps)
    cli.add_command(ppw.pypi_dl.dl_simple)
    cli.add_command(ppw.pypi_dl.search_scored)
    cli.add_command(ppw.pypi_dl.search)
    cli()
