from werkzeug.test import Client as BaseClient

from .helpers import pformat


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
        (('', True, 1), 1, 'args[0]', '{0!r}'),
        (('not', False, 0), 1, 'not args[0]', 'not {0!r}'),
        (('len', 'not len'),
            2, '{0}(args[1]) == args[0]', '{2}({1!r}) == {0!r}'
        ),
    )

    def __call__(self, operand, *args, **kwargs):
        '''Helper for assertion in test.'''
        for expr in self.expressions:
            if operand not in expr[0]:
                continue

            if len(args) < expr[1]:
                AttributeError(
                    'For %r operand need minimum %s arguments'
                    % (operand, expr[1])
                )
            params = list(args[:expr[1]]) + [operand]
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
            assert eval(expr[2].format(operand)), message
            return

        raise AttributeError('Use some of\n%s' % pformat(self.expressions))

    def raises(self, *args, **kwargs):
        from nose import tools
        tools.assert_raises(*args, **kwargs)

aye = Aye()
