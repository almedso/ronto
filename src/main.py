#!/usr/bin/env python3
import argparse
import subprocess
import sys
import os

import ronto
import ronto.init
import ronto.docker

def main():

    parser = argparse.ArgumentParser(
            prog='ronto',
            description="Yocto build wrapper")
    parser.add_argument('-f', '--file',
            help="Use alternative Rontofile",
            default='Rontofile.yml',
            type=argparse.FileType())
    parser.add_argument('-v', '--verbose',
            action='store_true',
            help="Increase output verbosity")
    parser.add_argument('--version', action="version",
            version=ronto.__version__,
            help="Print program version")
    subparsers = parser.add_subparsers(help='sub-command help')

    ronto.init.add_command(subparsers)
    ronto.docker.add_command(subparsers)

    args = parser.parse_args()
    ronto.set_verbosity(args.verbose)

    if 'func' in args:
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

