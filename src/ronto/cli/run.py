import subprocess
import sys
import shlex
import os

from ronto import dryrun,verbose
from ronto.model import get_value_with_default, potentially_replace_by_var

def _compose_command_prefix(args):
    command = ['ronto']
    if args.file and args.file.name != 'ronto.yml':
        command.append('--file')
        command.append(args.file.name)
    if args.verbose:
        command.append('--verbose')
    if args.dryrun:
        command.append('--dryrun')
    if args.env:
        for env in args.env:
            command.append('--env')
            command.append(env)
    return command


def process(args):
        verbose(f"Run script '{args.script}'")
        if args.script == 'all':
            script = get_value_with_default(['scripts', 'all'],
                ['fetch --force', 'init --rebuild-conf', 'build'])
        else:
            script = get_value_with_default(['scripts', args.script])
        if script == None or not isinstance(script, list):
            print(f"Script '{args.script}' not found")
            sys.exit(1)
        for step in script:
            command = _compose_command_prefix(args)
            command.extend(shlex.split(potentially_replace_by_var(step)))
            verbose(f"Run step {' '.join(command)}")
            if dryrun():
                print(f"dry: {' '.join(command)}")
            else:
                try:
                    proc = subprocess.Popen(command, check=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
                    while proc.returncode is None:
                        # handle output by direct access to stdout and stderr
                        for line in process.stdout:
                            print(line)
                        # set returncode if the process has exited
                        process.poll()
                except subprocess.CalledProcessError as err:
                    print(f"Error in processing step {err}")
                    sys.exit(1)
        verbose(f"Script '{args.script}' successfully finished")


def add_command(subparser):
    parser = subparser.add_parser(
        "run",
        help="""
        Run a ronto "script".
        """,
    )
    parser.add_argument("script", type=str, default="all", nargs='?',
            help="Script to run - default script is 'all'"),
    parser.set_defaults(func=process)
