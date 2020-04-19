import glob
import os
import sys

from ronto import verbose, run_cmd
from . import exists, get_value_with_default
from .builder import get_targets


def publish_root_dir():
    """
    check if publishing is configured and
    returns publish root directory if so
    otherwise None.
    """
    if exists(['publish']):
        dir = get_value_with_default(['publish', 'webserver_host_dir'])
        if dir != None:
            return dir
        return get_value_with_default(['docker', 'publish_dir', 'container'])
    return None


def publish_package_dir():
    """
    checks if publishing of packages configured
    and if so it returns the directory to publish
    to (full path) or None
    """
    root_dir = publish_root_dir()
    if root_dir != None:
        rel_dir = get_value_with_default(['publish', 'package_dir'], 'feeds')
        return os.path.join(root_dir, rel_dir)
    return None


def publish_image_dir():
    """
    checks if publishing of images configured
    and if so it returns the directory to publish
    to (full path) or None
    """
    root_dir = publish_root_dir()
    if root_dir != None:
        rel_dir = get_value_with_default(['publish', 'package_dir'], 'images')
        return os.path.join(root_dir, rel_dir)
    return None

def source_package_dir():
    """
    Determine source package directory and return it.
    Assumption is that there is just one distro i.e. tmp-<distro>
    So far only ipk is supported.
    """
    build_dir = get_value_with_default(['build', 'build_dir'], 'build')
    out_dir_pattern = os.path.join(os.getcwd(), build_dir, 'tmp-*', 'deploy', 'ipk')
    output_dirs = glob.glob(out_dir_pattern)
    if len(output_dirs) == 0:
        print('There is no "ipk" package directory')
        sys.exit(1)
    if len(output_dirs) > 1:
        print('There are multiple distributions - do know which is relevant')
        sys.exit(1)
    return output_dirs[0]


def image_files(target):
    files = []
    machine = get_value_with_default(['machine'], model=target)
    image = get_value_with_default(['image'], model=target)
    # publish may contain a list of image types to copy separated by ':'
    # if no image type is given wic is assumed
    image_types = []
    if exists(['publish']):
        image_types = get_value_with_default(['publish'], 'wic', model=target).split(':')
    build_dir = get_value_with_default(['build', 'build_dir'], 'build')
    out_dir_pattern = os.path.join(os.getcwd(), build_dir, 'tmp-*', 'deploy', 'images', machine)
    output_dirs = glob.glob(out_dir_pattern)
    if len(output_dirs) == 0:
        print('There is no image output directory')
        sys.exit(1)
    if len(output_dirs) > 1:
        print('There are multiple distributions - do know which is relevant')
        sys.exit(1)
    for extension in image_types:
        files.append(os.path.join(output_dirs[0], image + '-' + machine + '.' + extension))
    return files


def publish_packages():
    if get_value_with_default(["build", "packageindex"]):
        publish_dir = publish_package_dir()
        if publish_dir != None:
            # make sure directories are available
            os.makedirs(publish_dir, exist_ok=True)
            # we assume rsync is installed
            run_cmd(['rsync', '-ah', source_package_dir(), publish_dir])


def publish_target(target):
    publish_dir = publish_image_dir()
    if publish_dir != None:
        # make sure directories are available
        os.makedirs(publish_dir, exist_ok=True)
        if 'publish' in target:
            for image_machine in image_files(target):
                verbose(f"Publish target {os.path.basename(image_machine)}")
                run_cmd(['cp', '-fL', image_machine, publish_dir])


def publish_images(targets_file=None, target=None):
    """
    Publish images and packages depending on the configuration in ronto.yml.
    It is possible to overwrite packaging configuration in ronto.yml
    by giving an alternative targets_file or a single target.
    """
    if target:
        targets = [target]
    else:
        targets = get_targets(targets_file)
    for target in targets:
        publish_target(target)
