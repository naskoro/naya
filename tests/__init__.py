def test_helpers():
    '''
    NOTICE: Need doctest

    >>> from os import getcwd
    >>> from naya import App
    >>> app = App('getcmd')
    >>> assert app.root_path == getcwd()
    '''


def test_jinja():
    '''
    NOTICE: Need doctest

    >>> from naya.base import App
    >>> from examples import small
    >>> app = App(__name__)
    >>> app.jinja
    False
    '''
