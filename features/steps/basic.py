import subprocess
import os
import shutil
import re
import tempfile
from behave import *
import parse


use_step_matcher("cfparse")



@parse.with_pattern(r"finally\s+")
def parse_word_finally(text):
    """Type converter for "finally " (followed by one/more spaces)."""
    return text.strip()

register_type(finally_=parse_word_finally)


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


@when('I {:finally_?}enter "{cli}"')
def step_impl(context, finally_, cli):
    rontofile = []
    if hasattr(context, 'rontofile'):
        rontofile = ['--file', context.rontofile ]
    command = COMMAND + rontofile + cli.split()
    context.command = command
    try:
        output = subprocess.check_output(command)
        context.output = output.decode().split('\n')
    except subprocess.CalledProcessError as err:
        context.exitcode = err.returncode
        context.output = err.output.decode().split('\n')
    if hasattr(context, 'rontofile') and finally_:
        # cleanup temporary rontofile after command was running "finally"
        os.remove(context.rontofile)


@then('the exit code indicates an error')
def step_impl(context):
    assert hasattr(context, 'exitcode')


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
    if hasattr(context, 'command'):
        print(f"Command run: {context.command}")
    expected = context.text.split('\n')
    print(f"expected: {expected}")
    assert hasattr(context, 'output')
    print(f"output: {context.output}")
    assert len(context.output) >= len(expected)
    for i in range(len(expected)):
        print(f"Index: {i}, {expected[i]}")
        assert match_line(expected[i], context.output[i])


@given(u'empty sources')
def step_impl(context):
    if os.path.isdir('sources'):
        shutil.rmtree('sources')