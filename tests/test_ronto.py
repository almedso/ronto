import pytest

import ronto
from ronto.model import check_version, VersionError

def test_version():
    """ check ronto exposes a version attribute """
    assert hasattr(ronto, "__version__")
    assert isinstance(ronto.__version__, str)


def test_rontofile_version_ok():
    check_version(1)
    check_version('1')
    check_version(None)

def test_rontofile_version__fail_wrong_format():
    with pytest.raises(VersionError):
        check_version("1.2.3")

def test_rontofile_version__fail_too_high():
    with pytest.raises(VersionError):
        check_version(2)
