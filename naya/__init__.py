import os

from werkzeug import (
    SharedDataMiddleware, ClosingIterator,
    Response as BaseResponse, Request as BaseRequest
)
from werkzeug.exceptions import HTTPException
from werkzeug.routing import Map, Rule, Submount

from .conf import Config
from .ext.jinja import JinjaMixin
from .helpers import get_package_path, register


class Module(object):
    def __init__(self, import_name, theme=None):
        if not theme:
            theme = {'path_suffix': '_theme', 'endpoint': 'theme'}
        if isinstance(theme, dict):
            theme = Config(theme)

        self.theme = theme
        self.import_name = import_name
        self.root_path = get_package_path(self.import_name)

        theme_path = self.get_path(theme['path_suffix'])
        self.theme_path = os.path.isdir(theme_path) and theme_path or None

        self.url_map = Map()
        self.url_views = {}

    @property
    def url_rules(self):
        return self.url_map.iter_rules()

    def build_endpoint(self, endpoint):
        return '%s:%s' % (self.import_name, endpoint)

    def add_route(self, rule, endpoint, view_func=None, **options):
        if endpoint.find(':') == -1:
            endpoint = self.build_endpoint(endpoint)
        options['endpoint'] = endpoint
        self.url_map.add(Rule(rule, **options))
        if view_func:
            self.url_views[endpoint] = view_func

    def route(self, rule, **options):
        def decorator(func):
            endpoint = options.pop('endpoint', func.__name__)
            self.add_route(rule, endpoint, func, **options)
            return func
        return decorator

    def get_path(self, *args):
        args = list(args)
        args.insert(0, self.root_path)
        return os.path.join(*args)

    def __str__(self):
        return u'%s' % self.import_name

    def __repr__(self):
        return '<naya.Module(%s)>' % self


class Response(BaseResponse):
    default_mimetype = 'text/html'


class Request(BaseRequest):
    pass


class BaseApp(object):
    request_class = Request
    response_class = Response

    def __init__(self, prefs):
        if isinstance(prefs, basestring):
            prefs = {'modules': {'': Module(prefs)}}

        self.conf = self.get_prefs(prefs)

        self.root = self.conf['modules:']
        self.modules = self.conf['modules']

        for init_func in register.get_funcs(self, 'init'):
            init_func()

    @register('default_prefs')
    def default_prefs(self):
        return {
            'debug': False,
            'theme': {
                'path_suffix': '_theme',
                'endpoint': 'theme',
                'url_prefix': '/s/',
            },
            'modules': {},
        }

    def get_prefs(self, prefs_):
        prefs = Config()
        for func in register.get_funcs(self, 'default_prefs'):
            prefs.update(func())

        prefs.update(prefs_)
        return prefs

    @register('init')
    def init_modules(self):
        for name, module in self.modules.items():
            if self.root == module:
                continue

            self.root.url_views.update(module.url_views)
            self.root.url_map.add(
                Submount('/%s' % name, module.url_rules)
            )

    @register('init')
    def init_shares(self):
        shares = []
        for name, module in self.modules.items():
            if not module.theme_path:
                continue
            prefix = '%s%s' % (self.conf['theme:url_prefix'], name)
            prefix = '%s' % prefix.rstrip('/')
            self.root.add_route(
                '%s/<path:path>' % prefix,
                module.build_endpoint(self.conf['theme:endpoint']),
                build_only=True
            )
            shares.append((prefix, module.theme_path))

        shares.reverse()
        for prefix, path in shares:
            self.dispatch = SharedDataMiddleware(self.dispatch, {prefix: path})

    def url_for(self, endpoint, **values):
        prefix = endpoint.find(':')
        if prefix != -1:
            suffix = endpoint[prefix:]
            prefix = endpoint[0:prefix]
            if prefix in self.modules:
                module = self.modules[prefix]
                endpoint = '%s%s' % (module.import_name, suffix)
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

    def pre_dispatch(self, environ):
        self.request = Request(environ)
        self.url_adapter = self.root.url_map.bind_to_environ(environ)

    def dispatch(self, environ, start_response):
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
        self.pre_dispatch(environ)
        return self.dispatch(environ, start_response)


class App(BaseApp, JinjaMixin):
    pass
