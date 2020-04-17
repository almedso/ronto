import os
import sys
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
    if variables:
        verbose(f"CLI environment parameters: {variables}")
        cli_variables_ = dict(var.split('=') for var in variables)


def read_rontofile(file):
    global model_
    verbose("Read ronto.yml")
    model_ = yaml.load(file, Loader=yaml.FullLoader)
    update_defaults()
    check_version(get_value(['version'], model_))


class VersionError(Exception):
    pass


def check_version(version):
    if version != None:
        try:
            verbose(f"Check rontofile version {version}")
            int_version = int(version)
            if int_version > 1:
                raise VersionError()
        except ValueError:
            raise VersionError()


def env_val(key, value):
    env = os.getenv(key)
    if env:
        verbose(f"Read from environment {key}: {env}")
        return env
    else:
        return value


def _get_variable(key):
    if key in cli_variables_:
        return cli_variables_[key]
    if key in variables_:
        return variables_[key]
    return None


class VarNotKnownError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = 'unknown'


def _potentially_replace_by_var_single(data):
    """ This function throws an exception if var not found """
    p = re.compile(r'.*(\{\{ *([A-Za-z]+) *\}\})')
    m = p.match(data)
    if m:
        replacement = m.group(1)
        value = _get_variable(m.group(2))
        if value:
            data = data.replace(replacement, value)
        else:
            raise VarNotKnownError(m.group(2))
    return data


def _potentially_replace_by_var(data):
    # we need to support two replacements
    # so just call the single replacement twice
    return _potentially_replace_by_var_single(
            _potentially_replace_by_var_single(data))

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


def exists(descriptor: List[str], model=None):
    return get_value(descriptor, model, check_exists=True)


def get_value(descriptor: List[str], model=None, check_exists=False):
    """
    Get a value from the model specification (as read from ronto.yml)

    * Strings in the descriptor denote keys in a directory
    * injecting the model allows to parse sub areas obtained
    * from returned lists
    * Function acts also like an element exist checker.
    """
    if model == None:
        model = model_
    if len(descriptor) == 0:
        return None
    if not model or not isinstance(model, dict):
        return None
    if descriptor[0] in model:
        m = model[descriptor[0]]
        if len(descriptor) > 1:
            # recursive call
            return get_value(descriptor[1:], m)

        # here the value exists
        if check_exists:
            return True
        # just one entry left all other cases handled
        if isinstance(m, list):
            # lists are handled outside, thus return as they are
            return m
        if isinstance(m, int) or isinstance(m, float) or isinstance(m, bool):
            # primitives do not require var replacement
            return m
        if isinstance(m, str):
            return _potentially_replace_by_var(m)
    if check_exists:
        return False
    return None

def get_value_with_default(descriptor: List[str], default=None , model=None):
    try:
        value = get_value(descriptor, model)
    except VarNotKnownError as err:
        # not sure if that is a good idea and should be rather done
        # at docker closures/decorators
        print(f"Variable {err.message} not defined but needed by ronto.yml")
        sys.exit(1)
    if value != None:  # ask explicitely since e.g. False must be return as boolean value
        return value
    return default
