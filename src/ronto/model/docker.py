import array
import docker
import fcntl
import os
import pty
import re
import sys
import select
import tempfile
import termios
import tty

from pathlib import Path

from ronto import \
        dryrun, \
        is_command_available_or_exit, \
        is_in_docker, \
        run_cmd, \
        verbose
from . import get_value, get_value_with_default, exists


PROJECT_DIR_HOST = os.getcwd()
SSH_HOST = os.path.join(str(Path.home()), ".ssh")


class DockerConfig:

    _use_docker = False
    image = "almedso/yocto-bitbaker:latest"
    privatized_image = "my-yocto-bitbaker"

    project_dir_container = "/yocto/root"
    cache_dir_container = "/yocto/cache"
    cache_dir_host = os.path.abspath(os.path.join(PROJECT_DIR_HOST, "..", "cache"))
    publish_dir_container = "/yocto/publish"
    publish_dir_host = ""

    def __init__(cls):
        if exists(["docker"]):
            verbose("Docker configuration found")
            cls._use_docker = True
            cls.image = get_value_with_default(
                    ["docker", "image"], "almedso/yocto-bitbaker:latest")
            cls.privatized_image = get_value_with_default(
                    ["docker", "privatized_image"], "my-yocto-bitbaker")
            cls.project_dir_container = get_value_with_default(
                    ["docker", "project_dir"], "/yocto/root")
            cls.cache_dir_host = get_value_with_default(
                    ["docker", "cache_dir", "host"],
                    os.path.abspath(os.path.join(PROJECT_DIR_HOST, '..', 'cache')))
            cls.cache_dir_container = get_value_with_default(
                    ["docker", "cache_dir", "container"], "/yocto/cache")
            cls.publish_dir_host = get_value_with_default(
                    ["docker", "publish_dir", "host"],"")
            cls.publish_dir_container = get_value_with_default(
                    ["docker", "publish_dir", "container"], "/yocto/publish")

    def get_image(cls):
        return cls.image

    def get_privatized_image(cls):
        return cls.privatized_image

    def use_docker(cls):
        return cls._use_docker


def create_dir_and_dockerfile(
    yocto_bitbaker_image="almedso/yocto-bitbaker:latest", yocto_user_home="/home/yocto"
):
    """
    create a temporary directory and add a Dockerfile
    to create a privatized container
    """
    uid = os.getuid()
    gid = os.getgid()
    verbose(f"Inject uid {uid} and gid {gid}")
    dockerfile = f"""
        FROM {yocto_bitbaker_image}

        RUN pip3 install --upgrade ronto
        RUN groupadd --gid {gid} yocto || true && \
        useradd --uid {uid} --gid {gid} --home {yocto_user_home} \
                --create-home --shell /bin/bash yocto

        USER yocto
        """
    dir = tempfile.mkdtemp()
    filename = os.path.join(dir, "Dockerfile")
    with open(filename, "w") as f:
        f.write(dockerfile)
    return dir

def abs_path(path):
    if path[0] != '/':
        # relative path
        path = os.path.join(os.getcwd(), path)
    return os.path.abspath(path)

class DockerHost:
    """
    Only used if this runs on docker host

    As a constraint: the name of the container is the same
    is the name of the privatized image
    """

    def __init__(self, config):
        # skip totally if repo is not set.
        is_command_available_or_exit(["docker", "--version"])
        self.config = config
        self.docker = docker.from_env()  # create a docker client
        self.yocto_user_home = "/home/yocto"  # needed for consistency reasons
        # container name must be suffixed of something that identifies that
        # project root is mounted in - with use the "short" project directory
        self.container_name = \
            config.privatized_image + '-' + os.path.basename(os.getcwd())

    def build_privatized_docker_image(self):
        if dryrun():
            print(f"dry: Build or get privatized docker image: " \
                  f"{self.config.privatized_image}")
        else:
            try:
                image_label = self.config.privatized_image + ":latest"
                image = self.docker.images.get(image_label)
                verbose(f"Privatized image {image_label} exists" \
                            " - no need to build")
            except docker.errors.ImageNotFound as _err:
                self._build_privatized_docker_image()

    def _build_privatized_docker_image(self):
        verbose("Build privatized docker image")

        privatized_docker_image = self.config.get_privatized_image()
        yocto_docker_image = self.config.get_image()
        dir = create_dir_and_dockerfile(yocto_docker_image, self.yocto_user_home)
        if dryrun():
            with open(os.path.join(dir, "Dockerfile"), "r") as f:
                print("dry: privatizing Dockerfile" + f.read())
        run_cmd(["docker", "build", "-t", privatized_docker_image, dir])
        os.remove(os.path.join(dir, "Dockerfile"))  # cleanup Dockerfile
        os.rmdir(dir)  # cleanup temporary directory

    def create_container(self):
        containers = self.docker.containers.list(
            all=True, filters={"name": self.container_name}
        )
        if len(containers) == 1:
            verbose(f"Container already exists, reusing ...")
            self.container = containers[0]
            return

        verbose("Create docker container")
        if dryrun():
            print(f"dry: Build container: {self.container_name}")
        else:
            volumes = {
                os.getcwd(): {
                    "mode": "rw",
                    "bind": self.config.project_dir_container,
                },
                abs_path(self.config.cache_dir_host): {
                    "mode": "rw",
                    "bind": self.config.cache_dir_container,
                },
            }
            local_ssh_dir = os.path.join(Path.home(), ".ssh")
            if os.path.isdir(local_ssh_dir):
                # only if host (local) user has ssh configured inject
                volumes[local_ssh_dir] = {
                    "mode": "ro",
                    "bind": os.path.join(self.yocto_user_home, ".ssh"),
                }
            if self.config.publish_dir_host != "" and os.path.isdir(
                self.config.publish_dir_host
            ):
                # only if host (local) is configured and exists configure
                volumes[abs_path(self.config.publish_dir_host)] = {
                    "mode": "rw",
                    "bind": self.config.publish_dir_container,
                }
            self.container = self.docker.containers.create(
                detach=True,
                # Inject an infinite loop command
                command="bash -c 'while true; do sleep 1; done'",
                user=os.getuid(),
                read_only=False,  # otherwise /tmp is not writeable
                name=self.container_name,
                image=self.config.privatized_image,
                volumes=volumes,
            )
            verbose(f"Docker container created: {self.container}")

    def start_container(self):
        if dryrun():
            print(f"dry: Start container: {self.container_name}")
        else:
            verbose(f"Docker container status: {self.container.status}")
            if self.container.status != "running":
                verbose(f"Start docker container")
                self.container.start()
            # wait until container is running

    def run_command(self, command, interactive_flag=False):

        # cleanup the ronto command path
        if isinstance(command, list):
            if 'ronto' in command[0]:
                command[0] = 'ronto'  # get rid of of host local path
        if isinstance(command, str):
            p = re.compile('^([\w/]*ronto)')
            command = p.sub('ronto', command)

        if interactive_flag \
        or  '-i' in command \
        or '--interactive' in command: # in works on lists and on strings
            self.run_interactive_build_command(command)
        else:
            self.run_batch_command(command)
        verbose(f"Docker host - command '{command}' finished")


    def run_batch_command(self, command):
        verbose(f"Docker host - run batch command '{command}'")
        if dryrun():
            print(f"dry: (batch-in-container) {command}")
        else:
            socket = self.container.exec_run(cmd=command, stream=True,
                        demux=True, workdir=self.config.project_dir_container)
            for (stdout, stderr) in socket.output:
                if stdout:
                    sys.stdout.buffer.write(b'.')
                    sys.stdout.buffer.write(stdout)
                if stderr:
                    sys.stderr.buffer.write(b'+')
                    sys.stderr.buffer.write(stderr)

    def run_interactive_build_command(self, command):
        verbose(f"Docker host - run interactive command '{command}'")
        if dryrun():
            print(f"dry: (interactive-in-container) {command}")
        else:
            try:
                socket = self.container.exec_run(cmd=command, tty=True,
                            stdin=True, socket=True, demux=False,
                            workdir=self.config.project_dir_container)
                socket.output._sock.send(b'export PSADD="(c*r)"\n')
                while True:
                    r, w, e = select.select([sys.stdin, socket.output._sock],
                                        [], [sys.stdin, socket.output._sock])
                    if sys.stdin in r:
                        d = os.read(sys.stdin.fileno(), 10240)
                        socket.output._sock.send(d)
                    elif socket.output._sock in r:
                        data = socket.output._sock.recv(16384)
                        os.write(sys.stdout.fileno(), data)
                    if sys.stdin in e or socket.output._sock in e:
                        break  # leave the loop
            except Exception as err:
                verbose(f"Exception: {err}")

    def stop_container(self):
        if dryrun():
            print(f"dry: Stop container: {self.container_name}")
        else:
            verbose(f"Docker stop container")
            self.container.stop()

    def remove_container(self):
        if dryrun():
            print(f"dry: Remove container: {self.container_name}")
        else:
            self.container.remove(force=True)  # force for just to be sure

    def remove_privatized_image(self):
        self.remove_container()
        run_cmd(["docker", "rmi", self.config.get_privatized_image()])

    def remove_all(self):
        # do not use as ofter since it requires download of more than 1 GByte
        self.remove_container()
        run_cmd(["docker", "rmi", self.config.get_image()])


def docker_factory():
    docker_config = DockerConfig()
    if docker_config.use_docker():
        verbose(f"Docker context configured")
        if not is_in_docker():
            return DockerHost(docker_config)
        else:
            verbose(f"Run inside the container")
            return None
    verbose(f"Docker context not configured")
    return None


# a decorator that helps to run docker
def docker_context():
    def _docker_context(function):
        def __docker_context(*args, **kwargs):
            verbose(f"Docker decorator - started")
            docker = docker_factory()
            if docker:
                verbose("Invoke on docker context ...")
                docker.build_privatized_docker_image()
                docker.create_container()
                docker.start_container()
                command = sys.argv
                result = docker.run_command(command)
                docker.stop_container()
            else:
                verbose("Do not run on docker")
                result = function(*args, **kwargs)
            verbose(f"Docker decorator - done")
            return result

        return __docker_context

    return _docker_context
