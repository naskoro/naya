def test_aye():
    '''
    FAIL: Need Doctest for test_testing.test_aye;

    >>> from naya.testing import aye
    >>> aye('==', 1, 1)
    >>> aye('!=', 1, 2)
    >>> aye('==', 'test', 'test1')
    Traceback (most recent call last):
        ...
    AssertionError: assert 'test' == 'test1'
    >>> aye('==', 1, 2)
    Traceback (most recent call last):
        ...
    AssertionError: assert 1 == 2
    >>> aye('!=', 1, 1)
    Traceback (most recent call last):
        ...
    AssertionError: assert 1 != 1
    >>> aye(True, 1)
    >>> aye('', 0)
    Traceback (most recent call last):
        ...
    AssertionError: assert 0
    >>> aye(True, 0)
    Traceback (most recent call last):
        ...
    AssertionError: assert 0
    >>> aye(True, 0, message='It is not True')
    Traceback (most recent call last):
        ...
    AssertionError: assert 0, It is not True
    >>> aye(True, 0, 'It is not True')
    Traceback (most recent call last):
        ...
    AssertionError: assert 0
    ('It is not True',)
    >>> aye(True, 0, m='It is not True')
    Traceback (most recent call last):
        ...
    AssertionError: assert 0
    {'m': 'It is not True'}
    >>> aye('not', 0, m='It is False')
    >>> aye('not', 1, m='It is not False')
    Traceback (most recent call last):
        ...
    AssertionError: assert not 1
    {'m': 'It is not False'}
    >>> aye(False, 1, m='It is not False')
    Traceback (most recent call last):
        ...
    AssertionError: assert not 1
    {'m': 'It is not False'}
    >>> aye('in', '42', 'answer 42')
    >>> aye('in', '13', 'answer 42')
    Traceback (most recent call last):
        ...
    AssertionError: assert '13' in 'answer 42'
    >>> aye('not in', '13', 'answer 42')
    >>> aye('no in', '13', 'answer 42')
    Traceback (most recent call last):
        ...
    AttributeError: Use some of
    ((('==', '!=', '>', '<', '>=', '<=', '<>', 'in', 'not in', 'is', 'not is'),
      2,
      'args[0] {0} args[1]',
      '{0!r} {2} {1!r}'),
     (('', 'true', True, 1), 1, 'args[0]', '{0!r}'),
     (('not', 'false', False, 0), 1, 'not args[0]', 'not {0!r}'))
    '''
