import subprocess
import os
import re
import tempfile
from behave import *


COMMAND = ['python', '-m', 'ronto.main' ]


def match_line(expected, line):
    m = re.search(expected, line)
    return m != None


@given(u'ronto is installed')
def step_impl(context):
    command = COMMAND + ['--help']
    with open(os.devnull, 'w')  as FNULL:
        result = subprocess.run(command, stdout=FNULL)
    assert 0 == result.returncode


@when('I enter "{cli}"')
def step_impl(context, cli):
    rontofile = []
    if hasattr(context, 'rontofile'):
        rontofile = ['--file', context.rontofile ]
    command = COMMAND + rontofile + cli.split()
    output = subprocess.check_output(command)
    context.output = output.decode().split('\n')
    if hasattr(context, 'rontofile'):
        # cleanup after command was running
        os.remove(context.rontofile)


@then(u'ronto prints "{version}"')
def step_impl(context, version):
    assert context.failed is False
    assert context.output[0] == version


@given('a rontofile content as')
def step_impl(context):
    with tempfile.NamedTemporaryFile(mode='w', delete=False,) as f:
        f.write(context.text)
        context.rontofile = f.name


@then(u'ronto prints')
def step_impl(context):
    expected = context.text.split('\n')
    print(f"expected: {expected}")
    assert hasattr(context, 'output')
    print(f"output: {context.output}")
    assert len(context.output) >= len(expected)
    for i in range(len(expected)):
        print(f"Index: {i}, {expected[i]}")
        assert match_line(expected[i], context.output[i])
