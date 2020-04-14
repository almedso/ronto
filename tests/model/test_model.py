import pytest

import ronto.model
from ronto.model import _potentially_replace_by_var, get_value


def test_get_model():
    model = ronto.model.get_model()
    assert ronto.model.model_ == model


def test_potentially_replace_by_var__no_match():
    assert 'foo' == _potentially_replace_by_var('foo')
    assert 'foo {{  }}' == _potentially_replace_by_var('foo {{  }}')

def test_potentially_replace_by_var__successful_match():
    ronto.model.cli_variables_ = {
        'FOO': 'bar'
    }
    assert 'bar' == _potentially_replace_by_var('{{FOO}}')
    assert 'bar' == _potentially_replace_by_var('{{ FOO }}')
    assert 'bar' == _potentially_replace_by_var('{{  FOO  }}')
    assert 'bar' == _potentially_replace_by_var('{{  FOO}}')
    assert 'bar' == _potentially_replace_by_var('{{FOO  }}')

    assert ' bar ' == _potentially_replace_by_var(' {{ FOO }} ')
    assert 'foo bar foo' == _potentially_replace_by_var('foo {{ FOO }} foo')
    assert 'bar foo' == _potentially_replace_by_var('{{FOO  }} foo')
    assert 'foo bar' == _potentially_replace_by_var('foo {{ FOO }}')

def test_potentially_replace_by_var__missing_var():
    with pytest.raises(Exception):
        _potentially_replace_by_var('{{BAR}}')


def test_get_value__ok():
    model = {
        'foo': {'bar': 'foobar', 'foo': '{{FOO}}'},
        'bar': {'foo': {'foo': [1, 2, 3]}}
    }
    ronto.model.cli_variables_ = {
        'FOO': 'bar'
    }
    assert 'foobar' == get_value(['foo', 'bar'], model=model)
    assert 'bar' == get_value(['foo', 'foo'], model=model)
    assert [1, 2, 3] == get_value(['bar', 'foo', 'foo'], model=model)

def test_get_value__fail():
    model = {
        'foo': {'bar': 'foobar', 'foo': '{{FOO}}'},
        'bar': {'foo': {'foo': [1, 2, 3]}}
    }
    assert None  == get_value([], model=model)
    assert None  == get_value(['foobar'], model=model)
    assert None  == get_value(['foo', 'foobar'], model=model)
    assert None  == get_value(['bar', 'foobar'], model=model)
    assert None  == get_value(['foo', 'bar', 'foo'], model=model)