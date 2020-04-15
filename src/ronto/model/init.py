import os
from shutil import copyfile, rmtree
from abc import ABC, abstractmethod

from ronto import verbose, dryrun, run_cmd
from ronto.model import get_model, get_value, get_value_with_default


def get_init_build_dir():
    BUILD_DIR = "build"  # default from poky
    return get_value_with_default(["build", "build_dir"], BUILD_DIR)


def get_init_script():
    INIT_SCRIPT = "sources/poky/oe-init-build-env"  # default from poky
    return get_value_with_default(["build", "init_script"], INIT_SCRIPT)


class SiteConfigHandler:
    def __init__(self):
        self.sitefile = get_value_with_default(["build", "site", "file"], "site.conf")
        verbose(f"Use site configuration file: {self.sitefile}")
        self.build_dir = get_init_build_dir()

    def handle(self):
        """
        Update site.conf if overwrite and file available
        Create site.conf if source file available
        """
        dest_config_dir = os.path.join(os.getcwd(), self.build_dir, "conf")
        dest_site_conf_file = os.path.join(dest_config_dir, "site.conf")
        if not os.path.isfile(dest_site_conf_file):
            # site.conf file does not exit (Create scenario)
            src_site_conf_file = os.path.join(os.getcwd(), self.sitefile)
            if os.path.isfile(src_site_conf_file):
                verbose(f"Create site.conf from: {src_site_conf_file}")
                if dryrun():
                    print(f"copy {src_site_conf_file} to {dest_site_conf_file}")
                else:
                    os.makedirs(dest_config_dir, exist_ok=True)
                    copyfile(src_site_conf_file, dest_site_conf_file)


def init_to_source_in() -> str:
    """
    Deliver the commandline that must be sourced as init.

    returns is e.g.  "TEMPLATECONF=template/dir source script build_dir"
    """
    script = get_init_script()
    template_dir = get_value_with_default(["build", "template_dir"])
    build_dir = get_init_build_dir()

    source_line = ""
    if template_dir != None:
        source_line += "TEMPLATECONF="
        source_line += os.path.join(os.getcwd(), template_dir) + " "
    source_line += "source " + script + " " + build_dir + "\n"
    return source_line


def run_init():
    """
    Source the init script once to place/ update build dir structure
    i.e. create build dir, conf dir and add local.conf, bblayer.conf
    """
    source_line = init_to_source_in()
    verbose(f"Run init: {source_line[:-1]}")
    run_cmd(["bash", "-c", source_line])


def clean_init(rebuild_conf=True, clean_conf_dir=False, clean_build_dir=False):
    build_dir = get_init_build_dir()
    config_dir = os.path.join(build_dir, "conf")
    if rebuild_conf:
        verbose(f"Remove local.conf and bblayers.conf in {config_dir}")
        try:
            os.remove(os.path.join(os.getcwd(), config_dir, "local.conf"))
        except FileNotFoundError:
            pass
        try:
            os.remove(os.path.join(os.getcwd(), config_dir, "bblayers.conf"))
        except FileNotFoundError:
            pass
    if clean_conf_dir:
        verbose(f"Remove configuration directory (cleanup) {config_dir}")
        rmtree(os.path.join(os.getcwd(), config_dir), ignore_errors=True)
    if clean_build_dir:
        verbose(f"Remove build directory (cleanup) {build_dir}")
        rmtree(os.path.join(os.getcwd(), build_dir), ignore_errors=True)
