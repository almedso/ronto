import subprocess
import sys
import os

from ronto import verbose
from ronto.model.builder import InteractiveBuilder, TargetBuilder
from ronto.model.docker import docker_context

from .fetch import process as fetch_process
from .init import init_process


@docker_context()
def build_process(args):
    verbose("Process build command")
    if args.interactive and not args.list_targets:
        builder = InteractiveBuilder()
    else:
        builder = TargetBuilder()
    if args.list_targets:
        builder.list_targets()
    else:
        builder.build()

def process(args):
    if args.fetch:
        args.force = True
        fetch_process(args)
    if args.init:
        args.rebuild_conf = False
        args.clean_build = False
        args.clean_conf = True
        init_process(args)
    build_process(args)

def add_command(subparser):
    parser = subparser.add_parser(
        "build",
        help="""
            Actually build something

            source the environment and use bitbake.
            """,
    )
    parser.add_argument(
        "--fetch",
        help="Run fetch command (with forced option) before build",
        action="store_true",
    )
    parser.add_argument(
        "-l", "--list-targets",
        help="List all targes that are subject to 'batch' build" \
             " - it overwrites --interactive option",
        action="store_true",
    )

    parser.add_argument(
        "--init",
        help="Run init command (with clean_conf option) before build",
        action="store_true",
    )
    parser.add_argument(
        "-i",
        "--interactive",
        help="Ignore targets and operate interactively",
        action="store_true",
    )
    parser.set_defaults(func=process)
