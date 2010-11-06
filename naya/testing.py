from nose import tools
from werkzeug.test import Client as BaseClient

from . import Response
from .helpers import pformat


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
            if operand in expr[0]:
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
        tools.assert_raises(*args, **kwargs)

aye = Aye()
