import os

from werkzeug import Response as ResponseBase, Request
from werkzeug.exceptions import HTTPException
from werkzeug.routing import Map, Rule
from werkzeug.wsgi import SharedDataMiddleware, ClosingIterator

from .helpers import get_package_path


class Module(object):
    def __init__(self, import_name):
        self.import_name = import_name
        self.root_path = get_package_path(self.import_name)

        self.url_map = Map()
        self.url_views = {}

    @property
    def url_rules(self):
        return self.url_map.iter_rules()

    def add_route(self, rule, endpoint, view_func=None, **options):
        endpoint = '%s:%s' % (self.import_name, endpoint)
        if view_func:
            endpoint = endpoint
        options['endpoint'] = endpoint
        self.url_map.add(Rule(rule, **options))
        if view_func:
            self.url_views[endpoint] = view_func

    def route(self, rule, **options):
        def decorator(func):
            endpoint = options.get('endpoint', func.__name__)
            self.add_route(rule, endpoint, func, **options)
            return func
        return decorator

    def get_path(self, *args):
        args = list(args)
        args.insert(0, self.root_path)
        return os.path.join(*args)


class Config(object):
    def __init__(self, prefs={}):
        self._prefs = prefs

    def __getattribute__(self, name):
        if name.startswith('_'):
            return object.__getattribute__(self, name)
        res = self._prefs[name]
        if isinstance(res, dict):
            res = Config(res)
        return res

    def __setattribute__(self, name, value):
        if name.startswith('_'):
            object.__setattribute__(self, name, value)
        self._prefs[name] = value


class Response(ResponseBase):
    default_mimetype = 'text/html'


class App(object):
    request_class = Request
    response_class = Response

    def __init__(self, root_module, prefs=None):
        self.set_root(root_module)
        self.conf = self.get_prefs(prefs)
        self.init()

    def init(self):
        from jinja2 import Environment, FileSystemLoader
        self.jinja = Environment(
            loader=FileSystemLoader(self.conf.theme.path)
        )

        self.root.add_route(
            '%s<path:path>' % self.conf.theme.url_prefix,
            self.conf.theme.endpoint,
            build_only=True
        )
        self.dispatch = SharedDataMiddleware(self.dispatch, {
            self.conf.theme.url_prefix: self.conf.theme.path
        })

    def set_root(self, module):
        if not isinstance(module, Module):
            module = Module(module)
        self.root = module

    @property
    def default_prefs(self):
        return {
            'debug': False,
            'theme': {
                'path': self.root.get_path('_theme'),
                'endpoint': 'theme',
                'url_prefix': '/s/',
            }
        }

    def get_prefs(self, prefs_):
        prefs = self.default_prefs
        if prefs_:
            prefs_ = prefs_(self) if callable(prefs_) else prefs_
            prefs.update(prefs_)
        return Config(prefs)

    def url_for(self, endpoint, **values):
        if endpoint.startswith(':'):
            endpoint = '%s%s' % (self.root.import_name, endpoint)
        return self.url_adapter.build(endpoint, values)

    def make_response(self, response):
        """
        Converts the return value from a view function to a real
        response object that is an instance of :attr:`response_class`.
        """
        if response is None:
            raise ValueError('View function did not return a response')
        if isinstance(response, self.response_class):
            return response
        if isinstance(response, basestring):
            return self.response_class(response)
        if isinstance(response, tuple):
            return self.response_class(*response)
        return self.response_class.force_type(response, self.request.environ)

    def dispatch(self, environ, start_response):
        self.request = Request(environ)
        self.url_adapter = self.root.url_map.bind_to_environ(environ)
        try:
            endpoint, values = self.url_adapter.match()
            handler = self.root.url_views[endpoint]
            response = handler(self, **values)
            response = self.make_response(response)
        except HTTPException, e:
            response = e

        response = self.make_response(response)
        return ClosingIterator(response(environ, start_response))

    def __call__(self, environ, start_response):
        return self.dispatch(environ, start_response)
