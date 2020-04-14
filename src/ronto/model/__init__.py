import os
import yaml
import re
from typing import List

from ronto import verbose

# module global variable
model_ = {}
# List of variables
variables_ = {}

# List of CLI injected variables
cli_variables_ = {}


def get_model():
    return model_


def set_variables(variables):
    global cli_variables_
    cli_variables_ = dict(var.split('=') for var in variables)


def read_rontofile(file):
    global model_
    verbose("Read Rontofile.yml")
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


def _get_variable(key):
    if key in cli_variables_:
        return cli_variables_[key]
    if key in variables_:
        return variables_[key]
    return None


def _potentially_replace_by_var(data):
    """ This function throws an exception if var not found """
    p = re.compile(r'.*(\{\{ *([A-Za-z]+) *\}\})')
    m = p.match(data)
    if m:
        replacement = m.group(1)
        value = _get_variable(m.group(2))
        if value:
            data = data.replace(replacement, value)
        else:
            raise Exception(f"Missing value for variable {m.group(1)}")
    return data


def update_defaults():
    """
    Section defaults to deal with, like:

    defaults:
        FOO: 'foo'
        BAR: 'bar'
    """
    global variables_
    verbose("Update default variables")
    if "defaults" in model_ and isinstance(model_["defaults"], dict):
        for default in model_["defaults"]:
            variables_[default] = env_val(default, model_["defaults"][default])


def get_value(descriptor: List[str], model=model_):
    """
    Get a value from the model specification (as read from Rontofile)

    * Strings in the descriptor denote keys in a directory
    * injecting the model allows to parse sub areas obtained
    * from returned lists
    """
    if len(descriptor) == 0:
        return None
    if not model or not isinstance(model, dict):
        return None
    if descriptor[0] in model:
        m = model[descriptor[0]]

        if len(descriptor) > 1:
            # recursive call
            return get_value(descriptor[1:], m)

        # just one entry left all other cases handled
        if isinstance(m, list):
            # lists are handled outside, thus return as they are
            return m
        if isinstance(m, str):
            return _potentially_replace_by_var(m)
    return None
