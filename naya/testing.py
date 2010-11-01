import re

from werkzeug.test import Client as BaseClient

from . import Response


class Client(BaseClient):
    def __init__(self, *args, **kwargs):
        if 'response_wrapper' not in kwargs and len(args) == 1:
            kwargs['response_wrapper'] = Response
        super(Client, self).__init__(*args, **kwargs)
        self.app = self.application


def go(method, status_code, *args, **kwargs):
    '''Helper for checking status code.'''
    rv = method(*args, **kwargs)
    kwargs['rv.data'] = rv.data
    aye('==', rv.status_code, status_code, *args, **kwargs)
    return rv


def aye(operand, *args, **kwargs):
    '''
    Helper for assertion in test.

    >>> aye('==', 1, 1)
    >>> aye('==', 1, 2)
    Traceback (most recent call last):
        ...
    AssertionError: assert 1 == 2
    >>> aye('in', 'test', 'test')
    >>> aye('not in', 'test', 'test')
    Traceback (most recent call last):
        ...
    AssertionError: assert 'test' not in 'test'
    >>> aye('==', 1, 2, 'No equal')
    Traceback (most recent call last):
        ...
    AssertionError: assert 1 == 2 >>> No equal
    >>> aye('==', 1, 2, 'No equal', really='No equal')
    Traceback (most recent call last):
        ...
    AssertionError: assert 1 == 2 >>> No equal
    ________________
    really = No equal
    >>> string = ''
    >>> aye(hasattr, string, '__str__')
    >>> aye(hasattr, string, 'name')
    Traceback (most recent call last):
        ...
    AssertionError: assert hasattr('', 'name')
    >>> aye(hasattr, string, 'name', _extra_='Has no attribute')
    Traceback (most recent call last):
        ...
    AssertionError: assert hasattr('', 'name') >>> Has no attribute
    >>> class Test():
    ...     pass
    ...
    >>> test = Test()
    >>> aye(test, 1, 1)
    Traceback (most recent call last):
        ...
    AttributeError: Bad arguments
    >>>
    '''
    def params_to_string(args, kwargs, pattern='%s'):
        params = [('%s = %s' % (key, value)) for key, value in kwargs.items()]
        params = tuple(list(args) + params)
        return [(pattern % param) for param in params] if params else params

    if isinstance(operand, basestring):
        condition = 'args[0] %s args[1]' % operand
        message = 'assert %r %s %r' % (args[0], operand, args[1])
        params = params_to_string(args[2:], kwargs)
        params = '\n________________\n'.join(params)
        message = '%s >>> %s' % (message, params) if params else message
        assert eval(condition), message
    elif hasattr(operand, '__call__'):
        extra_atr, extra = '_extra_', None
        if extra_atr in kwargs:
            extra = kwargs.pop(extra_atr)
        params = params_to_string(args, kwargs, '%r')
        params = ', '.join(params)
        message = 'assert %s(%s)' % (operand.__name__, params)
        message = '%s >>> %s' % (message, extra) if extra else message
        assert operand(*args, **kwargs), message
    else:
        raise AttributeError('Bad arguments')
