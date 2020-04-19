import pytest

import ronto.model
from ronto.model import potentially_replace_by_var, get_value, exists


def test_get_model():
    model = ronto.model.get_model()
    assert ronto.model.model_ == model


def testpotentially_replace_by_var__no_match():
    assert 'foo' == potentially_replace_by_var('foo')
    assert 'foo {{  }}' == potentially_replace_by_var('foo {{  }}')

def testpotentially_replace_by_var__successful_match():
    ronto.model.cli_variables_ = {
        'FOO': 'bar'
    }
    assert 'bar' == potentially_replace_by_var('{{FOO}}')
    assert 'bar' == potentially_replace_by_var('{{ FOO }}')
    assert 'bar' == potentially_replace_by_var('{{  FOO  }}')
    assert 'bar' == potentially_replace_by_var('{{  FOO}}')
    assert 'bar' == potentially_replace_by_var('{{FOO  }}')

    assert ' bar ' == potentially_replace_by_var(' {{ FOO }} ')
    assert 'foo bar foo' == potentially_replace_by_var('foo {{ FOO }} foo')
    assert 'bar foo' == potentially_replace_by_var('{{FOO  }} foo')
    assert 'foo bar' == potentially_replace_by_var('foo {{ FOO }}')

def testpotentially_replace_by_var__missing_var():
    with pytest.raises(Exception):
        potentially_replace_by_var('{{BAR}}')


def testpotentially_replace_by_two_vars__successful_match():
    ronto.model.cli_variables_ = {
        'FOO': 'foo',
        'BAR': 'bar'
    }
    assert 'foobar' == potentially_replace_by_var('{{FOO}}{{BAR}}')
    assert 'foobar' == potentially_replace_by_var('{{ FOO }}{{ BAR }}')
    assert ' foo x bar ' == potentially_replace_by_var(' {{ FOO }} x {{ BAR }} ')


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

def test_exists__ok():
    model = {
        'foo': {'bar': 'foobar', 'foo': '{{FOO}}'},
        'bar': {'foo': {'foo': [1, 2, 3]}}
    }
    ronto.model.cli_variables_ = {
        'FOO': 'bar'
    }
    assert exists (['foo', 'bar'], model=model)
    assert exists (['foo',], model=model)
    assert exists (['foo', 'bar'], model=model)
    assert not exists (['foo', 'bar', 'buf'], model=model)
    assert not exists (['foo', 'buf'], model=model)
    assert not exists (['buf'], model=model)
