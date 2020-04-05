
from ronto import verbose, run_cmd
from ronto.model import read_rontofile
from ronto.model.docker import docker_factory


def process(args):
    model = read_rontofile(args.file)
    docker = docker_factory(model)
    # only on docker host successful/usefull
    docker.build_privatized_docker_image()


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
    parser.set_defaults(func=process)
