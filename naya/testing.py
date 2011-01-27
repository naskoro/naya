import re
from pprint import pformat
from types import BuiltinFunctionType, FunctionType, MethodType

from werkzeug.test import Client as _Client


class Client(_Client):
    def __init__(self, *args, **kwargs):
        super(Client, self).__init__(*args, **kwargs)

        self.app = self.application
        if 'response_wrapper' not in kwargs and len(args) == 1:
            self.response_wrapper = self.app.response_class

    def open(self, *args, **kwargs):
        code = kwargs.pop('code', None)
        as_tuple = kwargs.pop('as_tuple', False)
        chain_info = kwargs.pop('chain_info', True)

        kwargs['as_tuple'] = True
        environ, response = super(Client, self).open(*args, **kwargs)

        if code:
            kwargs['as_tuple'] = as_tuple
            aye('==', code, response.status_code, *args, **kwargs)

        self.response = response
        self.request = self.app.request_class(environ)

        if chain_info:
            print('{0.url} ({0.method}, {0.status_code})'.format(self))
        if as_tuple:
            return environ, response
        return response

    def __getattr__(self, name):
        if name in ['data', 'content_type', 'status_code', 'headers']:
            if name == 'data':
                return self.response.data.decode(self.response.charset)
            return getattr(self.response, name)
        if name in ['path', 'url', 'method']:
            return getattr(self.request, name)
        raise AttributeError(name)

    def cssselect(self, selector, data=None):
        from lxml.html import fromstring, tostring

        def to_unicode(element):
            return tostring(
                element, encoding='utf-8', pretty_print=True
            ).decode('utf-8')

        if not data:
            data = self.data

        result = fromstring(data).cssselect(selector)
        return '\n\n'.join([to_unicode(row) for row in result])


class Aye(object):
    expressions = (
        (('==; !=; >; <; >=; <=; <>; in; not in; is; not is'.split('; ')),
            2, 'args[0] {0} args[1]', u'{0}{2}{1}'
        ),
        ((True, 1), 1, 'args[0]', u'{0}'),
        ((False, 0), 1, 'not args[0]', u'not{0}'),
    )

    def to_string(self, params_, prepare=True):
        params = []
        for param in params_:
            if isinstance(param, str):
                param = param.decode('utf-8')
            if not isinstance(param, unicode):
                param = pformat(param)
            if '\n' in param:
                param = u'\n<<<----------\n%s\n---------->>>\n' % param
            elif isinstance(param, unicode) and prepare:
                param = u" '%s' " % param
            else:
                param = u' %s ' % param
            params.append(param)
        return params

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
            params = self.to_string(required)
            params.append(operand)
            message = expr[3].format(*params)
            message = (message.strip(' ')).rstrip('\n')
            prefix = message.startswith('\n') and 'assert' or 'assert '
            message = prefix + message
            if 'message' in kwargs:
                message += ', %s' % kwargs.pop('message')
            message = [message]
            extra = args[expr[1]:]
            if extra:
                message += self.to_string(extra)
            if kwargs:
                message += self.to_string([pformat(kwargs)], prepare=False)
            message = ''.join(message)
            message = re.sub('\s$', '', message)
            message = message.encode('utf-8')
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
