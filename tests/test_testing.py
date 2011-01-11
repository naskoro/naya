# -*- coding: utf-8 -*-


def test_aye():
    u'''
    NOTICE: Need Doctest for test_testing.test_aye;

    >>> from naya.testing import aye, call, raises
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
    >>> aye(1, 0)
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
    AssertionError: assert 0 'It is not True'
    >>> aye(True, 0, m='It is not True')
    Traceback (most recent call last):
        ...
    AssertionError: assert 0 {'m': 'It is not True'}
    >>> aye(0, 0, m='It is False')
    >>> aye(0, 1, m='It is not False')
    Traceback (most recent call last):
        ...
    AssertionError: assert not 1 {'m': 'It is not False'}
    >>> aye(False, 1, m='It is not False')
    Traceback (most recent call last):
        ...
    AssertionError: assert not 1 {'m': 'It is not False'}

    >>> aye('in', '42', 'answer 42')
    >>> aye('in', 'тест', 'тест 42')
    >>> aye('in', u'тест', u'тест 42')
    >>> aye('in', '13', """answer 42
    ... new line
    ... new line""")
    Traceback (most recent call last):
        ...
    AssertionError: assert '13' in
    <<<----------
    answer 42
    new line
    new line
    ---------->>>
    >>> aye('in', '13', u"""answer 42
    ... new line
    ... new line""")
    Traceback (most recent call last):
        ...
    AssertionError: assert '13' in
    <<<----------
    answer 42
    new line
    new line
    ---------->>>
    >>> aye('==', '42', 42, """answer 42
    ... new line
    ... new line""")
    Traceback (most recent call last):
        ...
    AssertionError: assert '42' == 42
    <<<----------
    answer 42
    new line
    new line
    ---------->>>
    >>> aye('==', [('test', 'test')]*5, [('answer', 42)]*5)
    Traceback (most recent call last):
    ...
    AssertionError: assert
    <<<----------
    [('test', 'test'),
     ('test', 'test'),
     ('test', 'test'),
     ('test', 'test'),
     ('test', 'test')]
    ---------->>>
    ==
    <<<----------
    [('answer', 42),
     ('answer', 42),
     ('answer', 42),
     ('answer', 42),
     ('answer', 42)]
    ---------->>>
    >>> aye('not in', '13', 'answer 42')

    >>> aye('==', 1, call(len, ['1']), message='Cool')
    >>> aye('==', 0, call(len, ['1']), message='It is fail')
    Traceback (most recent call last):
        ...
    AssertionError: assert 0 == 1 len(['1']), It is fail
    >>> aye('!=', 0, call(len, ['1']), message='Cool')
    >>> aye('!=', 1, call(len, ['1']), message='It is fail')
    Traceback (most recent call last):
        ...
    AssertionError: assert 1 != 1 len(['1']), It is fail
    >>> aye('no in', '13', 'answer 42')
    Traceback (most recent call last):
        ...
    AttributeError: Use some of
    ((['==', '!=', '>', '<', '>=', '<=', '<>', 'in', 'not in', 'is', 'not is'],
      2,
      'args[0] {0} args[1]',
      u'{0}{2}{1}'),
     ((True, 1), 1, 'args[0]', u'{0}'),
     ((False, 0), 1, 'not args[0]', u'not{0}'))
    >>> aye('==', 42)
    Traceback (most recent call last):
    ...
    AttributeError: For '==' operand need minimum 2 arguments
    >>> aye(0)
    Traceback (most recent call last):
    ...
    AttributeError: For 0 operand need minimum 1 arguments
    >>> aye(True, call(isinstance, {}, dict))
    >>> aye(True, call(isinstance, {}, str))
    Traceback (most recent call last):
    ...
    AssertionError: assert False isinstance({}, <type 'str'>)
    >>> call(aye.__call__, 1, 1)
    None Aye.__call__(1, 1)
    >>> def answer(name='anonymous'):
    ...     return '%s, is %s' % (name, 42)
    >>> call(answer, name='naspeh')
    'naspeh, is 42' answer(name='naspeh')
    >>> call(answer)
    'anonymous, is 42' answer()
    >>> def check():
    ...     raise KeyError(2, 3)
    >>> raises(KeyError, check)
    KeyError(2, 3)
    >>> raises(KeyError, lambda: 1)
    Traceback (most recent call last):
    ...
    KeyError: 'Not raised'
    >>> aye('==', u'42', ('front', ''))
    Traceback (most recent call last):
    ...
    AssertionError: assert '42' == ('front', '')
    '''
