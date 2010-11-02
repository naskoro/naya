from werkzeug import Response as ResponseBase, Request as RequestBase


class Response(ResponseBase):
    default_mimetype = 'text/html'


class Request(RequestBase):
    pass


class Registry(object):
    def __init__(self):
        self.init_funcs = []

    def init(self, func):
        """Registers a function to run for initialization."""
        self.init_funcs.append(func)
        return func


registry = Registry()
