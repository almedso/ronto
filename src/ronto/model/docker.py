import os
import sys
import os
import tempfile
import docker
from pathlib import Path
from abc import ABC, abstractmethod

from ronto import verbose, run_cmd, dryrun, is_command_available_or_exit
from . import get_model


def is_in_docker():
    path = "/proc/self/cgroup"
    return (
        os.path.exists("/.dockerenv")
        or os.path.isfile(path)
        and any("docker" in line for line in open(path))
    )


PROJECT_DIR_HOST = os.getcwd()
SSH_HOST = os.path.join(str(Path.home()), ".ssh")


class DockerConfig:

    _use_docker = False
    image = "almedso/yocto-bitbaker:latest"
    privatized_image = "my-yocto-bitbaker"

    project_dir_container = "/yocto/root"
    cache_dir_container = "/yocto/cache"
    cache_dir_host = os.path.abspath(os.path.join(PROJECT_DIR_HOST, ".."))
    publish_dir_container = "/yocto/publish"
    publish_dir_host = ""

    def __init__(cls, model):
        if "docker" in model:
            cls._use_docker = True

            if isinstance(model["docker"], dict):
                if (
                    "image" in model["docker"]
                    and isinstance(model["docker"]["image"], str)
                    and model["docker"]["image"] != ""
                ):
                    cls.image = model["docker"]["image"]

                if (
                    "privatized_image" in model["docker"]
                    and isinstance(model["docker"]["privatized_image"], str)
                    and model["docker"]["privatized_image"] != ""
                ):
                    cls.privatized_image = model["docker"]["privatized_image"]

                if (
                    "project_dir" in model["docker"]
                    and isinstance(model["docker"]["project_dir"], str)
                    and model["docker"]["project_dir"] != ""
                ):
                    project_dir_container = model["docker"]["project_dir"]

                if "cache_dir" in model["docker"] and isinstance(
                    model["docker"]["cache_dir"], dict
                ):
                    if "host" in model["docker"]["cache_dir"] and isinstance(
                        model["docker"]["cache_dir"]["host"], str
                    ):
                        cache_dir_host = model["docker"]["cache_dir"]["host"]
                    if "container" in model["docker"]["cache_dir"] and isinstance(
                        model["docker"]["cache_dir"]["container"], str
                    ):
                        cache_dir_container = model["docker"]["cache_dir"]["container"]

                if "publish_dir" in model["docker"] and isinstance(
                    model["docker"]["publish_dir"], dict
                ):
                    if "host" in model["docker"]["publish_dir"] and isinstance(
                        model["docker"]["publish_dir"]["host"], str
                    ):
                        publish_dir_host = model["docker"]["publish_dir"]["host"]
                    if "container" in model["docker"]["publish_dir"] and isinstance(
                        model["docker"]["publish_dir"]["container"], str
                    ):
                        publish_dir_container = model["docker"]["publish_dir"][
                            "container"
                        ]

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

    def build_privatized_docker_image(self):
        try:
            image_label = self.config.privatized_image + ":latest"
            image = self.docker.images.get(image_label)
            verbose(f"Privatized image {image_label} exists - no need to build")
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
            all=True, filters={"name": self.config.privatized_image}
        )
        if len(containers) == 1:
            verbose(f"Container already exists, reusing ...")
            self.container = containers[0]
            return

        verbose("Create docker container")
        volumes = {
            os.getcwd(): {"mode": "rw", "bind": self.config.project_dir_container,},
            self.config.cache_dir_host: {
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
            volumes[self.config.publish_dir_host] = {
                "mode": "rw",
                "bind": self.config.publish_dir_container,
            }
        self.container = self.docker.containers.create(
            detach=True,
            # Inject an infinite loop command
            command="bash -c 'while true; do sleep 1; done'",
            # auto_remove=True, # since we fix the name no need to remove
            user=os.getuid(),
            read_only=True,
            name=self.config.privatized_image,
            image=self.config.privatized_image,
            volumes=volumes,
        )
        verbose(f"Docker container created: {self.container}")

    def start_container(self):
        verbose(f"Docker container status: {self.container.status}")
        if self.container.status != "running":
            verbose(f"Start docker container")
            self.container.start()
        # wait until container is running

    def run_command(self, command):
        verbose(f"Docker container status: {self.container.status}")
        verbose(f"Docker host - run command '{command}'")
        (exit_code, output) = self.container.exec_run(
            cmd=command,
            # tty=True,
            stdout=True,
            stderr=True,
            stream=True,
            workdir=self.config.project_dir_container,
        )
        verbose(f"Command exit code: {exit_code}")
        for line in output:
            verbose(line.decode())
        return output

    def stop_container(self):
        verbose(f"Docker stop container")
        self.container.stop()


def docker_factory(model):
    docker_config = DockerConfig(model)
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
            docker = docker_factory(get_model())
            if docker:
                verbose("Invoke on docker context ...")
                docker.build_privatized_docker_image()
                docker.create_container()
                docker.start_container()
                result = docker.run_command(sys.argv)
                docker.stop_container()
            else:
                verbose("Do not run on docker")
                result = function(*args, **kwargs)
            verbose(f"Docker decorator - done")
            return result

        return __docker_context

    return _docker_context
