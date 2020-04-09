from ronto import verbose, run_cmd
from ronto.model import get_model
from ronto.model.docker import docker_factory


def process(args):
    docker = docker_factory(get_model())
    # only on docker host successful/usefull
    if docker:
        docker.build_privatized_docker_image()
        docker.create_container()
        docker.start_container()
        docker.run_command(args.cmd)
        docker.stop_container()
    else:
        verbose("No docker environment")


def add_command(subparser):
    parser = subparser.add_parser(
        "docker",
        help="""
            Build localized docker image.

            Inside the personalized image a user 'yocto' exists
            with same GID/UID of the calling user. (this is
            required to inject ssh credential in users
            input image: docker -> image (or almedso/yocto-bitbaker:latest)
            input userhome: docker -> userhome (or /home/yocto)
            output image: always my-yocto-bitbaker
            """,
    )
    parser.add_argument("cmd", help="Run command", type=str)
    parser.set_defaults(func=process)
