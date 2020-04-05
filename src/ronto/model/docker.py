import os
import sys
import os
import tempfile
from pathlib import Path
from abc import ABC, abstractmethod

from ronto import verbose, run_cmd, dryrun_flag, is_command_available_or_exit
from . import model


def is_in_docker():
    path = '/proc/self/cgroup'
    return (
        os.path.exists('/.dockerenv') or
        os.path.isfile(path) and any('docker' in line for line in open(path))
    )

PROJECT_DIR_HOST = os.getcwd()
SSH_HOST = os.path.join(str(Path.home()), '.ssh')


class DockerConfig:

    _use_docker = False
    _use_privatized = False
    image = 'almedso/yocto-bitbaker:latest'
    privatized_image = 'my-yocto-bitbaker'

    project_dir_container = '/yocto/root'
    cache_dir_container = '/yocto/cache'
    cache_dir_host = os.path.abspath(os.path.join(PROJECT_DIR_HOST,'..'))
    publish_dir_container = '/yocto/publish'
    publish_dir_host = ''

    def __init__(cls, model):
        if 'docker' in model:
            cls._use_docker = True

            if isinstance(model['docker'], dict):
                if 'image' in model['docker'] \
                and isinstance(model['docker']['image'], str):
                    cls.image =  model['docker']['image']
                if 'privatized_image' in model['docker']:
                    cls._use_privatized = True
                    if isinstance(model['docker']['privatized_image'], str):
                        cls.privatized_image = model['docker']['privatized_image']

                if 'project_dir' in model['docker'] \
                and isinstance(model['docker']['project_dir'], str):
                    project_dir_container = model['docker']['project_dir']
                if 'cache_dir' in model['docker'] \
                and isinstance(model['docker']['cache_dir'], dict):
                    if 'host' in model['docker']['cache_dir'] \
                    and isinstance(model['docker']['cache_dir']['host'], str):
                        cache_dir_host = model['docker']['cache_dir']['host']
                    if 'container' in model['docker']['cache_dir'] \
                    and isinstance(model['docker']['cache_dir']['container'], str):
                        cache_dir_container = model['docker']['cache_dir']['container']
                if 'publish_dir' in model['docker'] \
                and isinstance(model['docker']['publish_dir'], dict):
                    if 'host' in model['docker']['publish_dir'] \
                    and isinstance(model['docker']['publish_dir']['host'], str):
                        publish_dir_host = model['docker']['publish_dir']['host']
                    if 'container' in model['docker']['publish_dir'] \
                    and isinstance(model['docker']['publish_dir']['container'], str):
                        publish_dir_container = model['docker']['publish_dir']['container']

    def get_image(cls):
        return cls.image

    def get_privatized_image():
        return cls.image

    def use_docker(cls):
        return cls._use_docker

    def use_privatized():
        return cls._use_privatized

class DockerInterface(ABC):
    """Public Interface only"""

    def __init__(self):
        super().__init__()

    @abstractmethod
    def build_privatized_docker_image(self):
        pass



class NoDocker(DockerInterface):
    """Basically a shortcut on everything"""

    def __init__(self):
        super().__init__()

    def build_privatized_docker_image(self):
        print('Docker not configured in Rontofile - abort')
        sys.exit(2)

class InsideContainer(DockerInterface):
    """Used when runs inside the container"""

    def __init__(self, config):
        self.config = config
        super().__init__()

    def build_privatized_docker_image(self):
        print('Does not make sense inside a container')
        sys.exit(2)


def create_dir_and_dockerfile(yocto_bitbaker_image='almedso/yocto-bitbaker:latest'):
    """
    create a temporary directory and add a Dockerfile
    to create a privatized container
    """
    uid = os.getuid()
    gid = os.getgid()
    verbose(f"Inject uid {uid} and gid {gid}")
    dockerfile = f"""
        FROM {yocto_bitbaker_image}

        RUN groupadd --gid {gid} yocto || true && \
        useradd --uid {uid} --gid {gid} --home /home/yocto --create-home --shell /bin/bash yocto

        USER yocto
        """
    dir = tempfile.mkdtemp()
    filename = os.path.join(dir, 'Dockerfile')
    with open(filename, 'w') as f:
        f.write(dockerfile)
    return dir


class DockerHost(DockerInterface):
    """Only used if this runs on docker host"""

    def __init__(self, config):
        # skip totally if repo is not set.
        is_command_available_or_exit( ['docker', '--version'])
        self.config = config
        super().__init__()

    def build_privatized_docker_image(self):
        verbose('Build privatized docker image')

        if not use_privatized():
            print("A privatized image are not configured - abort")
            return 1

        privatized_docker_image = self.config.get_privatized_image()
        verbose(f"Remove potentially old image: {privatized_docker_image}")
        run_cmd(['docker', 'rmi', privatized_docker_image ])
        yocto_docker_image = self.config.get_image()
        dir = create_dir_and_dockerfile(yocto_docker_image)
        run_cmd(['docker', 'build', '-t', privatized_docker_image, dir])
        if dryrun_flag:
            with open(os.path.join(dir, 'Dockerfile'),'r') as f:
                print("dry: privatizing Dockerfile" + f.read())
        os.remove(os.path.join(dir, 'Dockerfile'))  # cleanup Dockerfile
        os.rmdir(dir)  # cleanup temporary directory


def docker_factory(model):
    docker_config = DockerConfig(model)
    if docker_config.use_docker():
        if is_in_docker():
            return InsideContainer(docker_config)
        else:
            return DockerHost(docker_config)
    else:
        return NoDocker()
