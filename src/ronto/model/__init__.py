import os
import yaml

from ronto import verbose

model = {}
# List of variables
variables = {}

def read_rontofile(file):
    global model
    verbose('Read Rontofile.yml')
    model = yaml.load(file, Loader=yaml.FullLoader)
    update_defaults()
    return model


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
    Section defaults to deal with, like:

    defaults:
        FOO: 'foo'
        BAR: 'bar'
    """
    global variables
    verbose('Update default variables')
    if 'defaults' in model and isinstance(model['defaults'], dict):
        for default in model['defaults']:
            variables[default] = env_val(default, model['defaults'][default])
