"""
Builder around bitbake including init script

interactive shells within python:
https://stackoverflow.com/questions/41542960/run-interactive-bash-with-popen-and-a-dedicated-tty-python

collect output
https://janakiev.com/blog/python-shell-commands/

simple /bash context
https://www.saltycrane.com/blog/2011/04/how-use-bash-shell-python-subprocess-instead-binsh/
"""
import os
import sys
import select
import termios
import fcntl
import array
import tty
import pty
import subprocess
import yaml


from ronto import verbose, dryrun
from .init import get_init_build_dir, get_init_script
from ronto.model import get_value, get_value_with_default


class InteractiveContext:
    """Shell that can be initialized and runs bitbake inside its context"""

    def __init__(self, source_line):
        # establish the command
        command = ["bash", "-c", f"{source_line}; $SHELL"]
        verbose(f"{command}")

        # save original tty setting then set it to raw mode
        self.old_tty = termios.tcgetattr(sys.stdin)
        buf = array.array("h", [0, 0, 0, 0])
        fcntl.ioctl(sys.stdin, termios.TIOCGWINSZ, buf, True)
        tty.setraw(sys.stdin.fileno())
        self.master_fd, self.slave_fd = pty.openpty()
        fcntl.ioctl(self.slave_fd, termios.TIOCSWINSZ, buf)
        self.process = subprocess.Popen(
            command,
            preexec_fn=os.setsid,
            stdin=self.slave_fd,
            stdout=self.slave_fd,
            stderr=self.slave_fd,
        )
        # carridge return is required due to change terminal discipline
        verbose(f"Start Bash session: Pid {self.process.pid}\r")
        os.write(self.master_fd, b"export PS1='$PSADD(i*e b*d)> '\n")

    def run_context(self):
        # carridge return is required due to change terminal discipline
        verbose(f"run context\r")
        while self.process.poll() is None:
            r, w, e = select.select([sys.stdin, self.master_fd], [],
                                    [sys.stdin, self.master_fd])
            if sys.stdin in r:
                d = os.read(sys.stdin.fileno(), 10240)
                os.write(self.master_fd, d)
            elif self.master_fd in r:
                o = os.read(self.master_fd, 10240)
                if o:
                    os.write(sys.stdout.fileno(), o)
            if sys.stdin in e or self.master_fd in e:
                break

    def terminate(self):
        self.process.communicate()  # wait until exit is processed
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_tty)
        verbose(f"Stop bash session: Pid {self.process.pid}")
        self.process.terminate()  # maybe that is too much

    def __del__(self):
        # restore tty settings back
        self.process.kill()


class BatchContext:
    def __init__(self, source_line):
        self.process = subprocess.Popen( "bash", stdin=subprocess.PIPE)
        verbose(f"Start Bash session: Pid {self.process.pid}")
        self.run_context(source_line)

    def run_context(self, command):
        if dryrun():
            print(f"dry - Run build command: {command}")
        else:
            verbose(f"Run command: {command}")
            command += "\n"
            self.process.stdin.write(command.encode())

    def terminate(self):
        self.run_context("exit")
        self.process.communicate()  # wait until exit is processed
        verbose(f"Stop bash session: Pid {self.process.pid}")
        self.process.terminate()  # maybe that is to much

    def __del__(self):
        # to be sure not leaving any zombies
        self.process.kill()


class Builder:
    def __init__(self):
        script = get_init_script()
        self.build_dir = get_init_build_dir()

        # There is no need to source something with templatedir
        # this is done potentially in init command
        source_line = "source " + script + " " + self.build_dir
        verbose(f"Builder init sourcing: {source_line}")
        self.source_line = source_line


def get_targets_from_yaml_file(targets_file):
    """
    Read targets from file (either input or defined in ronto.yml )
    @target_file: relative path of targets file from project directory
                  or None
    @returns None of structure of the file
    """
    if not targets_file:
        targets_file = get_value_with_default(['build', 'targets_file'])
    if targets_file:
        verbose(f"Read targets from file: {targets_file}")
        try:
            with open(targets_file) as file:
                return yaml.load(file, Loader=yaml.FullLoader)
        except FileNotFoundError:
            print(f"File with target specifications not found -> fall back",
                    file=sys.stderr)
            return None
    return None


def verify_target_specification(raw_targets):
    verbose("Verify target specifications")
    targets = []
    if (raw_targets and isinstance(raw_targets, list)):
        for target in raw_targets:
            if (
                isinstance(target, dict)
                and "machine" in target
                and isinstance(target["machine"], str)
                and "image" in target
                and isinstance(target["image"], str)
            ):
                targets.append(target)
    return targets


def get_targets(targets_file):
    """ Get list of targets plus inspection of them """
    raw_targets = get_targets_from_yaml_file(targets_file)
    if not raw_targets:
        verbose("Check for targets directly defined in 'ronto.yml'")
        raw_targets = get_value(["build", "targets"])
    targets = verify_target_specification(raw_targets)
    if len(targets) == 0:
        verbose("  No verified target found -> use default target")
        # Add a default machine/image combination as of yocto docu
        # getting started section.
        targets.append({"machine": "qemux86", "image": "core-image-sato"})
    return targets


class TargetBuilder(Builder):
    def __init__(self, targets_file=None):
        verbose(f"Target Builder")
        super().__init__()
        self.targets = get_targets(targets_file)
        self.do_packageindex = get_value_with_default(
            ["build", "packageindex"], True)
        self.context = BatchContext(self.source_line)

    def build(self):
        for target in self.targets:
            # print instead of verbose since bitbake is verbose anyway
            print(f"****************************************************")
            print(f"* Build {target['image']} for {target['machine']}")
            print(f"****************************************************")
            self.context.run_context(
                f"MACHINE={target['machine']} bitbake {target['image']}"
            )
        if self.do_packageindex:
            verbose("Do package index")
            self.context.run_context("bitbake package-index")
        self.context.terminate()

    def list_targets(self):
        for target in self.targets:
            print(f"Machine: {target['machine']} Image: {target['image']}")


class InteractiveBuilder(Builder):
    def __init__(self):
        verbose(f"Interactive Builder")
        super().__init__()
        self.context = InteractiveContext(self.source_line)

    def build(self):
        self.context.run_context()
        self.context.terminate()  # it waits until the interactive session ends
