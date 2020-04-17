from ronto import verbose, run_cmd
from ronto.model.docker import docker_factory


def process(args):
    docker = docker_factory()
    # only on docker host successful/usefull
    if docker:
        docker.build_privatized_docker_image()
        docker.create_container()
        docker.start_container()
        docker.run_command(args.cmd, args.interactive)
        docker.stop_container()
        if args.rm_container:
            docker.remove_container()
        if args.rm_priv_image:
            docker.remove_privatized_image()
        if args.rm_all:
            docker.remove_all()
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
    parser.add_argument(
        "-i",
        "--interactive",
        help="Run the command interactively. The command must provide " \
             "an interpreter like python or any shell",
        action="store_true",
    )
    parser.add_argument(
        "--rm-container",
        help="Remove the container after build",
        action="store_true",
    )
    parser.add_argument(
        "--rm-priv-image",
        help="Remove the container and the privatized image after build",
        action="store_true",
    )
    parser.add_argument(
        "--rm-all",
        help="Remove the container and the privatized image" \
             "and root image after build",
        action="store_true",
    )
    parser.add_argument("cmd", type=str, default="bash", nargs='?',
             help="Run command (default is bash shell)"),
    parser.set_defaults(func=process)
