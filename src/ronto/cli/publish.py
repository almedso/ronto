import subprocess
import sys
import os

from ronto import verbose
from ronto.model.docker import docker_context
from ronto.model.publish import publish_packages, publish_images


@docker_context()
def process(args):
    publish_packages()
    if args.only_packages:
        return
    target = None
    if args.image:
        ( image, machine ) = args.image.split(':')
        target = dict(image=image, machine=machine, publish=args.image_types)
    publish_images(target=target)


def add_command(subparser):
    parser = subparser.add_parser(
        "publish",
        help="""
            Copy build artifacts (packages and images)
            to specific publish folders
            """,
    )
    parser.add_argument(
        "-p",
        "--only-packages",
        help="Publish only package index - overwrites image option",
        action="store_true",
    )
    parser.add_argument(
        "-i",
        "--image",
        help="Publish single image format: image:machine ",
    )
    parser.add_argument(
        "-t",
        "--image-types",
        help="""
            Overwrite image types colon separated. Default is 'wic'
            Is only considered if image option is given as well
            """,
        default="wic",
    )
    parser.set_defaults(func=process)
