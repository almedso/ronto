import subprocess
import sys
import os

from ronto import verbose
from ronto.model.builder import InteractiveBuilder, TargetBuilder
from ronto.model.docker import docker_context


@docker_context()
def process(args):
    verbose("Process build command")
    if args.interactive:
        builder = InteractiveBuilder()
    else:
        builder = TargetBuilder(args.tty)
    builder.build()


def add_command(subparser):
    parser_pin = subparser.add_parser(
        "build",
        help="""
            Actually build something

            source the environment and use bitbake.
            """,
    )
    parser_pin.add_argument(
        "-i",
        "--interactive",
        help="Ignore targets and operate interactively",
        action="store_true",
    )
    parser_pin.add_argument(
        "-t",
        "--tty",
        help="Apply terminal mode",
        action="store_true",
    )
    parser_pin.set_defaults(func=process)
