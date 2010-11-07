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
    def __init__(self, import_name, prefs=None):
        self.import_name = import_name
        self.url_map = Map()
        self.url_views = {}

        self.conf = self.get_prefs(prefs)

        self.theme = self.conf['theme']
        self.root_path = get_package_path(self.import_name)

        theme_path = self.get_path(self.theme['path_suffix'])
        self.theme_path = os.path.isdir(theme_path) and theme_path or None

        self.modules = self.get_modules()

        for func in register.get(self, 'init'):
            func()

    def get_modules(self):
        modules = Config({'': (self, '')})
        for prefix, module in self.conf['submodules'].items():
            if not isinstance(module, (tuple, list)):
                module = module, prefix
            modules[prefix] = module
        return modules

    def get_prefs(self, prefs_):
        prefs = Config()
        for func in register.get(self, 'default_prefs'):
            prefs.update(func())

        prefs.update(prefs_)
        return prefs

    @register('default_prefs')
    def default_module_prefs(self):
        return {
            'theme': {
                'path_suffix': '_theme',
                'endpoint': 'theme',
                'url_prefix': '/s/',
            },
            'submodules': {},
        }

    @register('init')
    def init_modules(self):
        for name, module in self.modules.items():
            module, prefix = module
            self.url_views.update(module.url_views)
            self.url_map.add(
                Submount('/%s' % prefix, module.url_rules)
            )

    @register('init')
    def init_shares(self):
        shares = []
        for name, module in self.modules.items():
            module, prefix = module
            if not module.theme_path:
                continue

            if hasattr(module, 'shares') and module.shares:
                shares += [
                    ('%s/%s' % (share[0].rstrip('/'), prefix), share[1])
                    for share in module.shares
                ]

        if self.theme_path:
            shares.append(('', self))

        self.shares = shares
        self.shares.reverse()

    def share(self, module, prefix, endpoint):
        prefix = prefix.rstrip('/')
        self.add_route(
            '%s/<path:path>' % prefix,
            module.build_endpoint(endpoint),
            build_only=True
        )

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


class BaseApp(Module):
    request_class = Request
    response_class = Response

    @register('default_prefs')
    def default_app_prefs(self):
        return {
            'debug': False,
        }

    def url_for(self, endpoint, **values):
        prefix = endpoint.find(':')
        if prefix != -1:
            suffix = endpoint[prefix:]
            prefix = endpoint[0:prefix]
            if prefix in self.modules:
                module = self.modules[prefix][0]
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

    @register('init')
    def init_shares(self):
        super(BaseApp, self).init_shares()

        if not self.shares:
            return

        endpoint = self.conf['theme:endpoint']
        url_prefix = self.conf['theme:url_prefix']

        if not self.theme_path:
            self.share(self, url_prefix, endpoint)

        for prefix, module in self.shares:
            prefix = '%s/%s' % (url_prefix.rstrip('/'), prefix.lstrip('/'))
            self.share(module, prefix, endpoint)
            self.dispatch = SharedDataMiddleware(
                self.dispatch, {prefix: module.theme_path}
            )

    def pre_dispatch(self, environ):
        self.request = Request(environ)
        self.url_adapter = self.url_map.bind_to_environ(environ)

    def dispatch(self, environ, start_response):
        try:
            endpoint, values = self.url_adapter.match()
            handler = self.url_views[endpoint]
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
