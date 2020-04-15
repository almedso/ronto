import subprocess
import sys
import os

from ronto import verbose
from .fetch import process as fetch_process
from .init import process as init_process
from .build import process as build_process


def process(args):
    fetch_process()
    init_process()
    build_process()


def add_command(subparser):
    parser = subparser.add_parser(
        "all",
        help="""
        Like make all - run fetch, init, build, ...
        """,
    )
    parser.set_defaults(func=process)
