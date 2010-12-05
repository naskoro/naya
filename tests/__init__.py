def test_helpers():
    '''
    NOTICE: Need doctest

    >>> from os import getcwd
    >>> from naya import Naya
    >>> app = Naya('getcmd')
    >>> assert app.root_path == getcwd()
    '''


def test_jinja():
    '''
    NOTICE: Need doctest

    >>> from naya.base import Naya
    >>> app = Naya(__name__)
    >>> app.jinja
    False
    '''
