import subprocess
import sys
import os

from ronto import verbose
from ronto.model import get_model
from ronto.model.fetcher import GitFetcher, RepoFetcher
from ronto.model.builder import InteractiveBuilder, TargetBuilder
from ronto.model.docker import docker_context


@docker_context()
def process(args):
    verbose('Process build command')
    if args.interactive:
        builder = InteractiveBuilder(get_model())
    else:
        builder = TargetBuilder(get_model(), args.targets)
    builder.build()


def add_command(subparser):
    parser_pin = subparser.add_parser('build', help="""
            Actually build something

            source the environment and use bitbake.
            """)
    parser_pin.add_argument('-i', '--interactive',
            help='Iignore targets and operate interactively',
            action="store_true")
    parser_pin.add_argument('-t', '--targets',
            help='File that contains target definitions',
            action="store_true")
    parser_pin.add_argument('-b', '--clean-build',
            help='Remove build directory directory',
            action="store_true")
    parser_pin.set_defaults(func=process)
