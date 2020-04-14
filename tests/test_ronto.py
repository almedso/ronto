import pytest

import ronto


def test_version():
    """ check ronto exposes a version attribute """
    assert hasattr(ronto, "__version__")
    assert isinstance(ronto.__version__, str)
