#!/usr/bin/env python3
import argparse
import subprocess
import sys
import os
import traceback

import ronto
import ronto.cli.fetch
import ronto.cli.init
import ronto.cli.build
import ronto.cli.run
import ronto.cli.docker

from ronto.model import read_rontofile, VersionError, set_variables


def format_exception(e):
    exception_list = traceback.format_stack()
    exception_list = exception_list[:-2]
    exception_list.extend(traceback.format_tb(sys.exc_info()[2]))
    exception_list.extend(traceback.format_exception_only(sys.exc_info()[0],
                         sys.exc_info()[1]))

    exception_str = "Traceback (most recent call last):\n"
    exception_str += "".join(exception_list)
    # Removing the last \n
    exception_str = exception_str[:-1]

    return exception_str


def main():
    try:
        parser = argparse.ArgumentParser(
                prog='ronto',
                description="Yocto build wrapper " \
                        "(full documentation at: https://ronto.readthedocs.io)")
        parser.add_argument('-f', '--file',
                help="Use alternative Rontofile",
                default='ronto.yml',
                type=argparse.FileType())
        parser.add_argument('-v', '--verbose',
                action='store_true',
                help="Increase output verbosity")
        parser.add_argument('-d', '--dryrun',
                action='store_true',
                help="Print commands only")
        parser.add_argument('-e', '--env',
                type=str, action='append',
                help="Inject environment Variable e.g. FOO=bar")
        parser.add_argument('--version', action="version",
                version=ronto.__version__,
                help="Print program version")
        subparsers = parser.add_subparsers(help='sub-command help')

        ronto.cli.fetch.add_command(subparsers)
        ronto.cli.init.add_command(subparsers)
        ronto.cli.build.add_command(subparsers)
        ronto.cli.run.add_command(subparsers)
        ronto.cli.docker.add_command(subparsers)

        args = parser.parse_args()
        ronto.set_verbosity(args.verbose)
        ronto.set_dryrun(args.dryrun)
        set_variables(args.env)
        try:
            read_rontofile(args.file)
        except VersionError:
             print(f"Unsupported version of ronto.yml file")
             sys.exit(1)

        if 'func' in args:
            args.func(args)
        else:
            parser.print_help()
    except Exception as e:
        print("")
        print("Oh, Oh - No good :-( This is not supposed to happen.")
        print("Please file an issue at https://github.com/almedso/ronto/issues")
        print("by copying and pasting the content below")
        print("-------8<-----8<------")
        print(f"Ronto version: {ronto.__version__}")
        print(format_exception(e))


if __name__ == '__main__':
    main()
