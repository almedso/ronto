"""
 Wrapper around building stuff using repotool and Yocto
"""

__version__ = "1.1.0"

import subprocess
import os
import sys

verbose_flag = False
dryrun_flag = False


def dryrun():
    return dryrun_flag


def set_verbosity(flag):
    global verbose_flag
    verbose_flag = flag


def is_in_docker():
    path = "/proc/self/cgroup"
    return (
        os.path.exists("/.dockerenv")
        or os.path.isfile(path)
        and any("docker" in line for line in open(path))
    )

def verbose(*args):
    verbose_marker = "--* "
    path = "/proc/self/cgroup"
    if is_in_docker():
        # use a different marker if container
        verbose_marker = "*** "

    if verbose_flag:
        print(verbose_marker + "".join(map(str, args)))


def set_dryrun(flag):
    global dryrun_flag
    dryrun_flag = flag


def run_cmd(cmd):
    if dryrun_flag:
        print(f"dry working dir: {os.getcwd()}")
        print("dry: " + " ".join(cmd))
    else:
        subprocess.call(cmd)


def is_command_available_or_exit(cmd):
    try:
        with open(os.devnull, "w") as devnull:
            subprocess.call(cmd, stdout=devnull, stderr=devnull)
    except IOError as _err:
        print(f"Program {cmd[0]} is not available - aborting", file=sys.stderr)
        sys.exit(1)
