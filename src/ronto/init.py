import subprocess
import sys
import os

from . import verbose
from .model import read_rontofile


def process(args):
    verbose('Process init command')
    read_rontofile(args.file)


def add_command(subparser):
    parser_pin = subparser.add_parser('init', help="""
            Initialize a build environment such that bitbake can run afterwards.

            This includes:
            (optionally creating and starting the build container),
            (optionally initializing google repo, syncing all sources),
            Creating environment variables,
            "test"-calling the yoctoinit script
            """)
    parser_pin.add_argument('-s', '--overwrite-site',
            help='Overwrite site.conf, only if it exist',
            action="store_true")
    parser_pin.add_argument('-l', '--rebuild-conf',
            help='Rebuild local.conf and bblayers.conf',
            action="store_true")
    parser_pin.add_argument('-t', '--clean-tmp',
            help='Remove tmp directory',
            action="store_true")
    parser_pin.add_argument('-b', '--clean-build',
            help='Remove build directory directory',
            action="store_true")
    parser_pin.set_defaults(func=process)
