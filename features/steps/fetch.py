
from behave import *
import os

@then(u'"{git_dir}" contains a git repository')
def step_impl(context, git_dir):
    assert os.path.isdir(git_dir)
    assert os.path.isdir(os.path.join(git_dir, '.git'))
