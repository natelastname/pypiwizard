#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2025-01-11T19:37:18-05:00

@author: nate
"""
import logging
import sys

def get_logger(name: str):
    formatter = logging.Formatter(
        fmt=("[%(levelname)8s][%(filename)s:%(lineno)d]"
             "%(message)s")
    )
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_handler.setFormatter(formatter)
    stdout_handler.setLevel(logging.DEBUG)
    logger = logging.getLogger(name)
    logger.handlers = [stdout_handler]
    logger.setLevel(logging.DEBUG)
    return logger

def replace_me():
    print(__name__)
