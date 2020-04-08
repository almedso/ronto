import os
import yaml

from ronto import verbose

# module global variable
model_ = {}
# List of variables
variables = {}


def get_model():
    return model_


def read_rontofile(file):
    global model_
    verbose('Read Rontofile.yml')
    model_ = yaml.load(file, Loader=yaml.FullLoader)
    update_defaults()


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
    if 'defaults' in model_ and isinstance(model_['defaults'], dict):
        for default in model_['defaults']:
            variables[default] = env_val(default, model_['defaults'][default])
