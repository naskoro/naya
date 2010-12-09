from pprint import pformat
from types import BuiltinFunctionType, FunctionType, MethodType

from werkzeug.test import Client as BaseClient


class Client(BaseClient):
    def __init__(self, *args, **kwargs):
        super(Client, self).__init__(*args, **kwargs)

        self.app = self.application
        if 'response_wrapper' not in kwargs and len(args) == 1:
            self.response_wrapper = self.app.response_class

    def open(self, *args, **kwargs):
        code = kwargs.pop('code', None)
        as_tuple = kwargs.pop('as_tuple', False)

        kwargs['as_tuple'] = True
        environ, response = super(Client, self).open(*args, **kwargs)

        if code:
            aye('==', code, response.status_code, *args, **kwargs)

        self.response = response
        self.request = self.app.request_class(environ)
        if as_tuple:
            return environ, response
        return response

    def __getattribute__(self, name):
        if name in ['data', 'content_type', 'status_code', 'headers']:
            return getattr(self.response, name)
        if name in ['path', 'url']:
            return getattr(self.request, name)
        return BaseClient.__getattribute__(self, name)


class Aye(object):
    expressions = (
        (('==; !=; >; <; >=; <=; <>; in; not in; is; not is'.split('; ')),
            2, 'args[0] {0} args[1]', '{0!r} {2} {1!r}'
        ),
        ((True, 1), 1, 'args[0]', '{0!r}'),
        ((False, 0), 1, 'not args[0]', 'not {0!r}'),
    )

    def __call__(self, operand, *args, **kwargs):
        '''Helper for assertion in test.'''
        for expr in self.expressions:
            if operand not in expr[0]:
                continue

            if len(args) < expr[1]:
                raise AttributeError(
                    'For %r operand need minimum %s arguments'
                    % (operand, expr[1])
                )
            args = list(args)
            required = args[:expr[1]]
            params = required + [operand]
            message = expr[3].format(*params)
            message = 'assert %s' % message
            if 'message' in kwargs:
                message += ', %s' % kwargs.pop('message')
            message = [message]
            extra = args[expr[1]:]
            if extra:
                message += [pformat(extra)]
            if kwargs:
                message += [pformat(kwargs)]
            message = '\n'.join(message)
            for i in xrange(len(required)):
                if isinstance(args[i], Caller):
                    args[i] = args[i].run()
            assert eval(expr[2].format(operand)), message
            return

        raise AttributeError('Use some of\n%s' % pformat(self.expressions))

aye = Aye()


class Caller(object):
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        params = []
        if self.args:
            params += ['%s' % arg for arg in self.args]
        if self.kwargs:
            params += ['%s=%r' % (n, v) for n, v in self.kwargs.items()]
        params = ', '.join(params)

        func_str = self.func
        if isinstance(self.func, (BuiltinFunctionType, FunctionType)):
            func_str = func_str.__name__
        elif isinstance(self.func, MethodType):
            func_str = '{0.im_class.__name__}.{0.__name__}'.format(self.func)

        return '{0!r} {1}({2})'.format(self.run(), func_str, params)

    def run(self):
        return self.func(*self.args, **self.kwargs)


def call(func, *args, **kwargs):
    return Caller(func, *args, **kwargs)


def raises(expected, callback, *args, **kwargs):
    try:
        callback(*args, **kwargs)
    except expected as e:
        return e
    else:
        raise expected('Not raised')
