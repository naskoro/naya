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
    >>> app = App(small.app.import_name, {'jinja': {'shared': False}})
    >>> c = app.test_client(code=404)
    >>> assert c.get('/t/', code=404)
    '''
