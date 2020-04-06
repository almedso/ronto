import subprocess
import sys
import os

from ronto import verbose
from ronto.model import read_rontofile
from ronto.model.fetcher import GitFetcher, RepoFetcher
from ronto.model.init import SiteConfigHandler, run_init, clean_init

from ronto.model.docker import docker_factory

def process_xxx(args):
    model = read_rontofile(args.file)
    docker = docker_factory(model)
    # only on docker host successful/usefull
    docker.start_container()
    docker.run_command('init', args)


def process(args):
    verbose('Process init command')
    model = read_rontofile(args.file)
    git_fetcher = GitFetcher(model)
    git_fetcher.fetch()
    repo_fetcher = RepoFetcher(model)
    repo_fetcher.fetch()
    clean_init(model,
        rebuild_conf=args.rebuild_conf,
        clean_build_dir=args.clean_build)
    run_init(model)
    siteconf = SiteConfigHandler(model)
    siteconf.handle(args.overwrite_site)


def add_command(subparser):
    parser_pin = subparser.add_parser('init', help="""
            Initialize a build environment such that bitbake can run afterwards.

            This includes:
            (optionally creating and starting the build container),
            (optionally initializing google repo, syncing all sources),
            Creating environment variables,
            "test"-calling the yoctoinit script
            """)
    parser_pin.add_argument('-s', '--overwrite-site',
            help='Overwrite site.conf, only if it exist',
            action="store_true")
    parser_pin.add_argument('-l', '--rebuild-conf',
            help='Rebuild local.conf and bblayers.conf',
            action="store_true")
    parser_pin.add_argument('-b', '--clean-build',
            help='Remove build directory directory',
            action="store_true")
    parser_pin.set_defaults(func=process)
