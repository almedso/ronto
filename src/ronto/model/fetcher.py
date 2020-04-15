"""
Fetchers for simple git and repo
"""
import os
import sys
import shutil

from ronto import verbose, is_command_available_or_exit
from ronto import run_cmd
from ronto.model import get_model, get_value, get_value_with_default


class GitFetcher:

    repos = []

    def __init__(cls):
        """
        Initialize from Rontofile:
        Rontofile syntax is:
        git:
          - source_dir: sources/poky
            git_url: git://git.yoctoproject.org/poky
        """
        model = get_model()
        if "git" in model:
            # skip totally if git is not set.
            is_command_available_or_exit(["git", "--version"])
            if len(cls.repos) > 0:
                # is already initialized or git is not defined as fetcher
                return
            verbose(f"Config base: Git repositories")

            if isinstance(model["git"], list):
                for entry in model["git"]:
                    verbose(f"Configured git repo: {entry['git_url']}")
                    # we read directly since variable replacement does not
                    # make sense for repository specification
                    url = get_value(["git_url"], entry)
                    source = get_value(["source_dir"], entry)
                    if url and source:
                        cls.repos.append(dict(git_url=url, source_dir=source))
                    # if (
                    #    isinstance(entry, dict)
                    #    and "source_dir" in entry
                    #    and isinstance(entry["source_dir"], str)
                    #    and "git_url" in entry
                    #    and isinstance(entry["git_url"], str)
                    #):
                    #    cls.repos.append(entry)
            if len(cls.repos) == 0:
                # initialize with poky default if nothing is given
                cls.repos.append(
                    {
                        "source_dir": "sources/poky",
                        "git_url": "git://git.yoctoproject.org/poky",
                    }
                )

    def fetch(cls, force=None):
        project_dir = os.getcwd()
        for entry in cls.repos:
            source_path = os.path.join(project_dir, entry["source_dir"])
            clone = False
            if os.path.isdir(source_path):
                if force:
                    # remove first and clone later
                    verbose("Remove old sources - i.e. forced update")
                    shutil.rmtree(source_path)
                    clone = True
                else:
                    verbose(f"Update git repo: {entry['git_url']}")
                    os.chdir(source_path)
                    run_cmd(["git", "remote", "update"])
                    os.chdir(project_dir)
            else:
                clone = True
            if clone:
                verbose(f"Clone git repo: {entry['git_url']}")
                clone_path = os.path.abspath(os.path.join(source_path, ".."))
                os.makedirs(clone_path, exist_ok=True)
                os.chdir(clone_path)
                run_cmd(["git", "clone", entry["git_url"], source_path])
                os.chdir(project_dir)


class RepoFetcher:

    url = ""
    manifest = "default.xml"
    branch = "master"

    def __init__(cls):
        """
        Initialize from Rontofile:
        Rontofile syntax is:
        repo:
          url: git://host/git-manifest-repo.git
          manifest: release-xyz.xml
          branch: master
        """
        if 'repo' in get_model():
            # skip totally if repo is not set.
            is_command_available_or_exit(["repo", "--version"])
            verbose(f"Config base: Google manifest repository")
            cls.url = get_value(['repo', 'url'])
            if cls.url == None:
                print("repo URL cannot be determined", file=sys.stderr)
                sys.exit(1)
            cls.branch = get_value_with_default(["repo", "branch"], 'master')
            cls.manifest = get_value_with_default(["repo", "manifest"], 'default.xml')

    def fetch(cls, force=None):
        if cls.url != "":
            verbose(f"Init repo from {cls.url}")
            run_cmd(
                ["repo", "init", "-u", cls.url, "-m", cls.manifest, "-b", cls.branch]
            )
            force_sync = "--force-sync" if force else ""
            verbose(f"Sync repo {force_sync}")
            run_cmd(["repo", "sync", force_sync ])
