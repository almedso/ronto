import os
from shutil import copyfile, rmtree
from abc import ABC, abstractmethod

from ronto import verbose, dryrun, run_cmd


def get_init_build_dir(model):
    BUILD_DIR = "build"  # default from poky
    build_dir = BUILD_DIR
    if "build" in model and isinstance(model["build"], dict):
        if "build_dir" in model["build"] and isinstance(
            model["build"]["build_dir"], str
        ):
            build_dir = model["build"]["build_dir"]
            verbose(f"Bitbake build directory: {build_dir}")
    return build_dir


def get_init_template_dir(model):
    template_dir = None
    if "build" in model and isinstance(model["build"], dict):
        if "template_dir" in model["build"] and isinstance(
            model["build"]["template_dir"], str
        ):
            template_dir = model["build"]["template_dir"]
            verbose(f"Bitbake init template directory: {template_dir}")
    return template_dir


def get_init_script(model):
    INIT_SCRIPT = "sources/poky/oe-init-build-env"  # default from poky
    script = INIT_SCRIPT
    if "build" in model and isinstance(model["build"], dict):
        if "init_script" in model["build"] and isinstance(
            model["build"]["init_script"], str
        ):
            script = model["build"]["init_script"]
            verbose(f"Bitbake init script: {script}")
    return script


class SiteConfigHandler:
    def __init__(self, model):
        self.overwrite = False
        self.sitefile = "site.conf"  # relative to project directory
        if "build" in model and isinstance(model["build"], dict):
            if "site" in model["build"] and isinstance(model["build"]["site"], dict):
                if "overwrite" in model["build"]["site"]:
                    self.overwrite = model["build"]["site"]["overwrite"]
                    verbose(f"Overwrite site.conf: {self.overwrite}")
                if "file" in model["build"]["site"] and isinstance(
                    model["build"]["site"]["file"], str
                ):
                    self.sitefile = model["build"]["site"]["file"]
                    verbose(f"Use site configuration file: {self.sitefile}")
        self.build_dir = get_init_build_dir(model)

    def handle(self, overwrite_site=False):
        """
        Update site.conf if overwrite and file available
        Create site.conf if source file available
        """
        dest_config_dir = os.path.join(os.getcwd(), self.build_dir, "conf")
        dest_site_conf_file = os.path.join(dest_config_dir, "site.conf")
        if os.path.isfile(dest_site_conf_file):
            # site.conf file exists (Update scenario)
            src_site_conf_file = os.path.join(os.getcwd(), self.sitefile)
            if (self.overwrite or overwrite_site) and os.path.isfile(
                src_site_conf_file
            ):
                verbose(f"Overwrite site.conf")
                if dryrun():
                    print(f"copy {src_site_conf_file} to {dest_site_conf_file}")
                else:
                    copyfile(src_site_conf_file, dest_site_conf_file)
        else:
            # site.conf file does not exit (Create scenario)
            src_site_conf_file = os.path.join(os.getcwd(), self.sitefile)
            if os.path.isfile(src_site_conf_file):
                os.makedirs(dest_config_dir, exist_ok=True)
                verbose(f"Create site.conf from: {src_site_conf_file}")
                if dryrun():
                    print(f"copy {src_site_conf_file} to {dest_site_conf_file}")
                else:
                    copyfile(src_site_conf_file, dest_site_conf_file)


def init_to_source_in(model):
    script = get_init_script(model)
    template_dir = get_init_template_dir(model)
    build_dir = get_init_build_dir(model)

    source_line = ""
    if template_dir != None:
        source_line += "TEMPLATECONF="
        source_line += os.path.join(os.getcwd(), template_dir) + " "
    source_line += "source " + script + " " + build_dir + "\n"
    # return source_line.encode()  # to byte string
    return source_line


def run_init(model):
    """
    Source the init script once to place/ update build dir structure
    i.e. create build dir, conf dir and add local.conf, bblayer.conf
    """
    source_line = init_to_source_in(model)
    verbose(f"Run init: {source_line}")
    run_cmd(["bash", "-c", source_line])


def clean_init(model, rebuild_conf=True, clean_build_dir=False):
    build_dir = get_init_build_dir(model)
    if rebuild_conf:
        verbose(f"Remove local.conf and bblayers.conf")
        config_dir = os.path.join(os.getcwd(), build_dir, "conf")
        rmtree(os.path.join(config_dir, "local.conf"), ignore_errors=True)
        rmtree(os.path.join(config_dir, "bblayers.conf"), ignore_errors=True)
    if clean_build_dir:
        verbose(f"Remove build_dir (cleanup) {build_dir}")
        rmtree(os.path.join(os.getcwd(), build_dir), ignore_errors=True)
