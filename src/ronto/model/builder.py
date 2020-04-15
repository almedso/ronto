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


from ronto import verbose, dryrun
from .init import get_init_build_dir, get_init_script


class InteractiveContext:
    """Shell that can be initialized and runs bitbake inside its context"""

    def __init__(self, source_line):
        # establish the command
        command = ["bash", "-c", f"{source_line}; $SHELL"]
        verbose(f"bash -c {command}")

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
        os.write(self.master_fd, b"export PS1='(yocto interactive build)> '\n")

    def run_context(self):
        # carridge return is required due to change terminal discipline
        verbose(f"run context\r")
        while self.process.poll() is None:
            r, w, e = select.select([sys.stdin, self.master_fd], [], [])
            if sys.stdin in r:
                d = os.read(sys.stdin.fileno(), 10240)
                os.write(self.master_fd, d)
            elif self.master_fd in r:
                o = os.read(self.master_fd, 10240)
                if o:
                    os.write(sys.stdout.fileno(), o)

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
        self.process = subprocess.Popen(
            "bash", preexec_fn=os.setsid, stdin=subprocess.PIPE
        )
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
    def __init__(self, model):
        script = get_init_script()
        self.build_dir = get_init_build_dir()

        # There is no need to source something with templatedir
        # this is done potentially in init command
        source_line = "source " + script + " " + self.build_dir
        verbose(f"Builder init sourcing: {source_line}")
        self.source_line = source_line
        super().__init__()


def get_targets(model):
    targets = []
    verbose("Check for defined targets")
    if (
        "build" in model
        and isinstance(model["build"], dict)
        and "targets" in model["build"]
        and isinstance(model["build"]["targets"], list)
    ):
        for target in model["build"]["targets"]:
            verbose(f"  Found target: {target}")
            if (
                isinstance(target, dict)
                and "machine" in target
                and isinstance(target["machine"], str)
                and "image" in target
                and isinstance(target["image"], str)
            ):
                targets.append(target)
    if len(targets) == 0:
        verbose("  No target found -> use default target")
        # Add a default machine/image combination as of yocto docu
        # getting started section.
        targets.append({"machine": "qemux86", "image": "core-image-sato"})
    return targets


def get_packageindex(model):
    if (
        "build" in model
        and isinstance(model["build"], dict)
        and "packageindex" in model["build"]
    ):
        return True if model["build"]["packageindex"] else False
    return True  # The default is to create package index


class TargetBuilder(Builder):
    def __init__(self, model, _target):
        verbose(f"Target Builder")
        super().__init__(model)
        self.targets = get_targets(model)
        self.do_packageindex = get_packageindex(model)
        self.context = BatchContext(self.source_line)

    def build(self):
        for target in self.targets:
            verbose(f"Build {target['image']} for {target['machine']}")
            self.context.run_context(
                f"MACHINE={target['machine']} bitbake {target['image']}"
            )
        if self.do_packageindex:
            verbose("Do package index")
            self.context.run_context("bitbake package-index")
        self.context.terminate()


class InteractiveBuilder(Builder):
    def __init__(self, model):
        verbose(f"Interactive Builder")
        super().__init__(model)
        self.context = InteractiveContext(self.source_line)

    def build(self):
        self.context.run_context()
        self.context.terminate()  # it waits until the interactive session ends
