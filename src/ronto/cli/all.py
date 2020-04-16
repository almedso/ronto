import subprocess
import sys
import os

from ronto import verbose
from .fetch import process as fetch_process
from .init import init_process
from .build import build_process


def process(args):
    args.force = None
    fetch_process(args)
    args.rebuild_conf = False
    args.clean_build = False
    args.clean_conf = False
    init_process(args)
    args.interactive = False
    args.tty = False
    build_process(args)


def add_command(subparser):
    parser = subparser.add_parser(
        "all",
        help="""
        Like make all - run fetch, init, build, ...
        """,
    )
    parser.set_defaults(func=process)
