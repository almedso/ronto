
from behave import *
import os

@given(u'"{file}" exists')
def step_impl(context, file):
    full_path = os.path.join(os.getcwd(), file)
    dir = os.path.dirname(full_path)
    os.makedirs(dir, exist_ok=True)
    text = ''
    if context.text:
        text = context.text
    with open(file, "w") as f:
        f.write(text)


@then(u'"{file}" does not exist')
def step_impl(context, file):
    full_path = os.path.join(os.getcwd(), file)
    assert not os.path.exists(full_path)


@then(u'"{file}" does exist')
def step_impl(context, file):
    full_path = os.path.join(os.getcwd(), file)
    print(f"File path: {full_path}")
    assert os.path.exists(full_path)

@then(u'"{file}" does exist containing "{expected}"')
def step_impl(context, file, expected):
    full_path = os.path.join(os.getcwd(), file)
    print(f"File path: {full_path}")
    assert os.path.exists(full_path)
    with open(full_path) as f:
        content = f.read()
        print(f"Content found: {content} expected: {expected}")
        assert content.find(expected) != -1
