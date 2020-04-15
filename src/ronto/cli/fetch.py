import subprocess
import sys
import os

from ronto import verbose
from ronto.model.fetcher import GitFetcher, RepoFetcher
from ronto.model.docker import docker_context


@docker_context()
def process(args):
    verbose("Process fetch command")
    git_fetcher = GitFetcher()
    git_fetcher.fetch(args.force)
    repo_fetcher = RepoFetcher()
    repo_fetcher.fetch(args.force)


def add_command(subparser):
    parser = subparser.add_parser(
        "fetch",
        help="""
        Fetch all sources (repositories with layers and configuration).
        If neither git nor repo is configured, nothing is fetched.
        """,
    )
    parser.add_argument(
        "-f",
        "--force",
        help="""
            force an source update.
            Either performs a force-sync for repotool organized sources
            or remove all sources before for git cloning for git sources
            """,
        action="store_true",
    )
    parser.set_defaults(func=process)
