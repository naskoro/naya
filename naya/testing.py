from werkzeug.test import Client as BaseClient

from . import Response


class Client(BaseClient):
    def __init__(self, *args, **kwargs):
        if 'response_wrapper' not in kwargs and len(args) == 1:
            kwargs['response_wrapper'] = Response
        super(Client, self).__init__(*args, **kwargs)
        self.app = self.application


def params_to_string(args, kwargs, pattern='%s'):
    params = [('%s = %s' % (key, value)) for key, value in kwargs.items()]
    params = tuple(list(args) + params)
    return [(pattern % param) for param in params] if params else params


class Func(object):
    def __init__(self, func, *args, **kwargs):
        self.func
        self.args = args
        self.kwargs = kwargs
        params = params_to_string(args, kwargs, '%r')
        params = ', '.join(params)
        self.message = '%s(%s)' % (func.__name__, params)

    def __call__(self):
        return self.func(*self.args, **self.kwargs)


def go(method, status_code, *args, **kwargs):
    '''Helper for checking status code.'''
    rv = method(*args, **kwargs)
    kwargs['rv.data'] = rv.data
    aye('==', rv.status_code, status_code, *args, **kwargs)
    return rv


def aye(operand, *args, **kwargs):
    '''
    Helper for assertion in test.

    '''
    if isinstance(operand, basestring):
        condition = 'args[0] %s args[1]' % operand
        message = 'assert %r %s %r' % (args[0], operand, args[1])
        params = params_to_string(args[2:], kwargs)
        params = '\n________________\n'.join(params)
        message = '%s >>> %s' % (message, params) if params else message
        assert eval(condition), message
    else:
        raise AttributeError('Bad arguments')
