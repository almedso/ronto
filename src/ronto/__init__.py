"""
 Wrapper around building stuff using repotool and Yocto
"""

__version__ = "0.0.1"

import subprocess
import os
import sys

verbose_flag = False
dryrun_flag = False


def dryrun():
    return dryrun_flag


def set_verbosity(flag):
    global verbose_flag
    print(f"verbose {flag}")
    verbose_flag = flag

def verbose(*args):
    if verbose_flag:
        print("*** " + "".join(map(str,args)))


def set_dryrun(flag):
    global dryrun_flag
    print(f"dryrun {flag}")
    dryrun_flag = flag

def run_cmd(cmd):
    if dryrun_flag:
        print(f"dry working dir: {os.getcwd()}")
        print("dry: " + " ".join(cmd))
    else:
        subprocess.call(cmd)


def is_command_available_or_exit(cmd):
    try:
        with open(os.devnull, 'w') as devnull:
            subprocess.call(cmd, stdout=devnull, stderr=devnull)
    except IOError as _err:
        print(f"Program {cmd[0]} is not available - aborting", file=sys.stderr)
        sys.exit(1)
