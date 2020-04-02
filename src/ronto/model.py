
import os
import yaml

from . import verbose

model = {}
# List of variables
variables = {}

# this name is by convention
PRIVATIZED_DOCKER_IMAGE = "my-yocto-bitbaker"


def is_in_docker():
    path = '/proc/self/cgroup'
    return (
        os.path.exists('/.dockerenv') or
        os.path.isfile(path) and any('docker' in line for line in open(path))
    )

def read_rontofile(file):
    global model
    verbose('Read Rontofile.yml')
    model = yaml.load(file, Loader=yaml.FullLoader)
    update_defaults()
    verbose(model)


def env_val(key, value):
    env = os.getenv(key)
    if env:
        verbose(f"Read from environment {key}: {env}")
        return env
    else:
        verbose(f"Use default for {key}: {value}")
        return value


def update_defaults():
    """
    # Section defaults
    defaults:
      FOO: 'foo'
      BAR: 'bar'
    """
    global variables
    verbose('Update default variables')
    if 'defaults' in model and isinstance(model['defaults'], dict):
        for default in model['defaults']:
            variables[default] = env_val(default, model['defaults'][default])


def get_docker_imagename(default):
    if 'docker' in model and isinstance(model['docker'], dict):
        if 'image' in model['docker'] and isinstance(model['docker']['image'], str):
            return model['docker']['image']
    return default

def get_docker_privatized_imagename():
    if 'docker' in model and isinstance(model['docker'], dict):
        if 'privatized_image' in model['docker'] and isinstance(model['docker']['privatized_image'], str):
            return model['docker']['privatized_image']
    return PRIVATIZED_DOCKER_IMAGE

def use_docker():
    if 'docker' in model:
        verbose('Use docker')
        return True
    else:
        return False


def use_privatized():
    if 'docker' in model and isinstance(model['docker'], dict):
        if 'privatized_image' in model['docker']:
            verbose('Use privatized docker image')
            return True
    return False