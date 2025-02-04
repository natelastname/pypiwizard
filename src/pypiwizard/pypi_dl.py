#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2025-02-04T09:19:05-05:00

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

import asyncio
import aiohttp
import feud
import shlex
import pypiwizard as ppw

logger = ppw.util.get_logger(__name__)

def subproc(cmd):
    shlex.split(cmd)
    result = sp.call(cmd.strip(), shell=True, executable='/bin/bash')
    return result

outpath = os.path.join(os.environ['HOME'], "pypiwizard_sdists")
index_file = os.path.join(outpath, 'simple.json')
os.makedirs(outpath, exist_ok=True)


async def download_index():
    url = "https://pypi.org/simple/?format=application/vnd.pypi.simple.v1+json"
    async with aiohttp.ClientSession() as sesh:
        resp = await sesh.request("GET", url)
        data = await resp.json()
        with open(index_file, 'w+') as fp:
            fp.write(json.dumps(data, indent=2))
        return data

async def dl_tarball(sesh, tb):
    url = tb['url']
    resp = await sesh.request('GET', url=url)
    tb_path = os.path.join(outpath, tb['filename'])
    bits = await resp.content.read()
    with open(tb_path, "w+b") as fp:
        fp.write(bits)

    cmd = f"""
pushd '{outpath}' \
&& dtrx '{tb_path}' \
&& unlink '{tb_path}' \
&& popd
    """.strip()
    subproc(cmd)
    return

async def retrieve_project(sem0, sesh, proj_name):
    async with sem0:
        url = f"https://pypi.org/simple/{proj_name}/?format=application/vnd.pypi.simple.v1+json"
        resp = await sesh.request("GET", url)
        txt = await resp.text()
        if resp.headers.get('Content-Type') == 'text/html':
            return
            # TODO: handle this better

        data = json.loads(txt)
        tarballs = []
        wheels = []
        for item in data['files']:
            if item['filename'].endswith('.whl'):
                wheels.append(item)
                continue
            tarballs.append(item)
        ##############################################################
        if len(tarballs) == 0:
            return

        tarballs = sorted(tarballs, key=lambda item: item['upload-time'], reverse=True)
        tb = tarballs[0]
        await dl_tarball(sesh, tb)

        return wheels, tarballs



async def get_projects(projects: dict):
    sem0 = asyncio.Semaphore(5)
    async with aiohttp.ClientSession() as sesh:
        tasks = []
        for proj in projects:
            coro = retrieve_project(sem0, sesh, proj)
            task = asyncio.create_task(coro)
            tasks.append(task)
        res = await asyncio.gather(*tasks)

    return res



async def get_info(sem0, sesh, proj_name):
    url = f"https://pypi.org/pypi/{proj_name}/json"
    resp = await sesh.request('GET', url)
    meta = await resp.json()

    return meta

async def do_search(regex: str, index):
    sem0 = asyncio.Semaphore(5)
    async with aiohttp.ClientSession() as sesh:
        matched = {}
        tasks = []

        projects = index['projects']
        for i, proj in enumerate(projects):
            proj_name = proj['name']
            if not re.match(regex, proj_name.lower()):
                continue

            task = asyncio.create_task(get_info(sem0, sesh, proj_name))
            tasks.append(task)

        result = await asyncio.gather(*tasks)

        return result


def load_or_fetch_index(update_index:bool):
    if not update_index and os.path.exists(index_file):
        logger.info("Loading index file...")
        with open(index_file, 'r') as fp:
            data = json.loads(fp.read())
    else:
        logger.info("Retrieving pypi index...")
        data = asyncio.run(download_index())

    return data

class SimpleDl(feud.Group):
    """Download sdists from PyPi."""
    def dl(regex: str, *, update_index: bool = False, download: bool = False):
        """Download sdists via regex."""
        data = load_or_fetch_index(update_index)
        all_projects = data['projects']
        matched = {}
        for i, proj in enumerate(all_projects):
            proj_name = proj['name']
            if not re.match(regex, proj_name):
                continue
            matched[proj_name] = proj
            logger.info(f'{i:8}: {proj_name}')
        if not download:
            return
        asyncio.run(get_projects(matched))

    def search(regex: str, *, update_index: bool = False):
        """Search for packages by regex."""
        data = load_or_fetch_index(update_index)
        result = asyncio.run(do_search(regex, data))
        for item in result:
            if not 'info' in item:
                continue
            info = item['info']
            name = info['name']
            summary = info['summary']
            print(f"{name:50}: {summary}")

    def scored(regex: str, *, update_index: bool = False):
        """Retrieve the top 100 results."""
        data = load_or_fetch_index(update_index)
        result = asyncio.run(do_search(regex, data))
        scores = {}
        specs = {}
        rev = None
        for item in result:
            if not 'info' in item:
                continue
            info = item['info']
            name = info['name']
            specs[name] = item
            def get(d0, key):
                if key in d0 and d0[key]:
                    return len(d0[key])
                return 0
            # A decent heuristic popularity score
            # Ranks aiohttp as #1 out of thousands when you search for 'aio.*'
            rev = True
            score1 = get(item, 'urls')
            score2 = get(info, 'requires_dist')
            score3 = get(info, 'classifiers')
            score = score1+score2+score3
            scores[name] = score
            print(f"{name}: {score}")

        result = sorted(scores.items(), key=lambda item: item[1], reverse=rev)
        result = result[0:100]
        for i, (item, score) in enumerate(result):
            spec = specs[item]
            summary = spec['info']['summary']
            print(f"[{i:3}][{score:4}] {item} - {summary}")

if __name__ == "__main__":
    feud.run(SimpleDl)
