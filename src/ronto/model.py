
import os
import yaml

from . import verbose

model = None
# List of variables
variables = {}


def read_rontofile(file):
    global model
    verbose('Read Rontofile.yml')
    model = yaml.load(file, Loader=yaml.FullLoader)
    update_defaults()
    print(model)


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
    if 'defaults' in model:
        for default in model['defaults']:
            variables[default] = env_val(default, model['defaults'][default])
