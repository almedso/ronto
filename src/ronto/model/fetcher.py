"""
Fetchers for simple git and repo
"""
import os

from ronto import verbose, is_command_available_or_exit
from ronto import run_cmd


class GitFetcher:

    repos = []

    def __init__(cls, model):
        """
        Initialize from Rontofile:
        Rontofile syntax is:
        git:
          - source_dir: sources/poky
            git_url: git://git.yoctoproject.org/poky
        """
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
                    if (
                        isinstance(entry, dict)
                        and "source_dir" in entry
                        and isinstance(entry["source_dir"], str)
                        and "git_url" in entry
                        and isinstance(entry["git_url"], str)
                    ):
                        cls.repos.append(entry)
            if len(cls.repos) == 0:
                # initialize with poky default if nothing is given
                cls.repos.append(
                    {
                        "source_dir": "sources/poky",
                        "git_url": "git://git.yoctoproject.org/poky",
                    }
                )

    def fetch(cls):
        project_dir = os.getcwd()
        for entry in cls.repos:
            source_path = os.path.join(project_dir, entry["source_dir"])
            if os.path.isdir(source_path):
                verbose(f"Update git repo: {entry['git_url']}")
                os.chdir(source_path)
                run_cmd(["git", "remote", "update"])
                os.chdir(project_dir)
            else:
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

    def __init__(cls, model):
        """
        Initialize from Rontofile:
        Rontofile syntax is:
        repo:
          url: git://host/git-manifest-repo.git
          manifest: release-xyz.xml
          branch: master
        """
        if "repo" in model:
            # skip totally if repo is not set.
            is_command_available_or_exit(["repo", "--version"])
            verbose(f"Config base: Google manifest repository")
            if isinstance(model["repo"], dict):
                if "url" in model["repo"] and isinstance(model["repo"]["url"], str):
                    cls.url = model["repo"]["url"]
                if "manifest" in model["repo"] and isinstance(
                    model["repo"]["manifest"], str
                ):
                    cls.url = model["repo"]["manifest"]
                if "branch" in model["repo"] and isinstance(
                    model["repo"]["branch"], str
                ):
                    cls.url = model["repo"]["branch"]

    def fetch(cls):
        if cls.url != "":
            verbose(f"Init repo from {cls.url}")
            run_cmd(
                ["repo", "init", "-u", cls.url, "-m", cls.manifest, "-b", cls.branch]
            )
            verbose(f"Sync repo")
            run_cmd(["repo", "sync"])
