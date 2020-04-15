import subprocess
import sys
import os

from .fetch import process as fetch_process

from ronto import verbose
from ronto.model import get_model
from ronto.model.init import SiteConfigHandler, run_init, clean_init
from ronto.model.docker import docker_context


@docker_context()
def init_process(args):
    verbose("Process init command")
    clean_init(rebuild_conf=args.rebuild_conf,
            clean_conf_dir=args.clean_conf,
            clean_build_dir=args.clean_build)
    run_init()
    siteconf = SiteConfigHandler()
    siteconf.handle()


def process(args):
    if args.fetch:
        args.force = False
        fetch_process(args)
    init_process(args)


def add_command(subparser):
    parser = subparser.add_parser(
        "init",
        help="""
            Initialize a build environment such that bitbake can run afterwards.
            As a result, <build-dir> exists, local.conf, bblayer.conf and
            optionally site.conf are in the <build-dir>/conf directory.

            There are various options, to either reuse existing
            all controlled by ronto.yml.
            "test"-sourcing the yocto init script
            """,
    )
    parser.add_argument(
        "-f",
        "--fetch",
        help="Run fetch command before init",
        action="store_true",
    )
    parser.add_argument(
        "-l",
        "--rebuild-conf",
        help="Rebuild local.conf and bblayers.conf at init",
        action="store_true",
    )
    parser.add_argument(
        "-c",
        "--clean-conf",
        help="Remove conf directory before init",
        action="store_true",
    )
    parser.add_argument(
        "-b",
        "--clean-build",
        help="Remove build directory directory before init",
        action="store_true",
    )
    parser.set_defaults(func=process)
