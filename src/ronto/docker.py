import subprocess
import sys
import os
import tempfile

from . import verbose
from .model import read_rontofile, \
        get_docker_imagename, \
        get_docker_privatized_imagename, \
        use_docker, use_privatized


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


def cmd_run (cmd, dryrun=False):
    if dryrun:
        print("dry: " + " ".join(cmd))
    else:
        subprocess.call(cmd)


def process(args):
    verbose('Build privatized docker image')
    read_rontofile(args.file)

    if not use_docker() or not use_privatized():
        print("Either docker or privatized images are not configured - abort")
        return 1

    privatized_docker_image = get_docker_privatized_imagename()
    verbose(f"Remove potentially old image: {privatized_docker_image}")
    cmd_run(['docker', 'rmi', privatized_docker_image ], args.dryrun)
    yocto_docker_image = get_docker_imagename('almedso/yocto-bitbaker:latest')
    dir = create_dir_and_dockerfile(yocto_docker_image)
    cmd_run(['docker', 'build', '-t', privatized_docker_image, dir], args.dryrun)
    if args.dryrun:
        with open(os.path.join(dir, 'Dockerfile'),'r') as f:
             print("dry: privatizing Dockerfile" + f.read())
    os.remove(os.path.join(dir, 'Dockerfile'))  # cleanup Dockerfile
    os.rmdir(dir)  # cleanup temporary directory


def add_command(subparser):
    parser = subparser.add_parser('docker', help="""
            Build localized docker image.

            Inside the personalized image a user 'yocto' exists
            with same GID/UID of the calling user. (this is
            required to inject ssh credential in users
            input image: docker -> image (or almedso/yocto-bitbaker:latest)
            input userhome: docker -> userhome (or /home/yocto)
            output image: always my-yocto-bitbaker
            """)
    parser.add_argument('-d', '--dryrun',
            action='store_true',
            help="print commands only")
    parser.set_defaults(func=process)
