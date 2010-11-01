import os

from jinja2 import (
    Environment, TemplateNotFound,
    PrefixLoader as PrefixLoaderBase, FileSystemLoader
)
from werkzeug import (
    Response as ResponseBase, Request as RequestBase,
    SharedDataMiddleware, ClosingIterator
)
from werkzeug.exceptions import HTTPException
from werkzeug.routing import Map, Rule, Submount

from .helpers import get_package_path, DictByDot
from .wsgi import SharedJinjaMiddleware


class Module(object):
    def __init__(self, import_name, theme=None):
        if not theme:
            theme = {'path_suffix': '_theme', 'endpoint': 'theme'}
        if isinstance(theme, dict):
            theme = DictByDot(theme)

        self.theme = theme
        self.import_name = import_name
        self.root_path = get_package_path(self.import_name)

        theme_path = self.get_path(theme.path_suffix)
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


class Response(ResponseBase):
    default_mimetype = 'text/html'


class Request(RequestBase):
    pass


class PrefixLoader(PrefixLoaderBase):
    def get_source(self, environment, template):
        for prefix, loader in self.mapping.items():
            path = template
            if path.startswith(prefix):
                path = template[len(prefix):]
            path = path.lstrip('/')
            try:
                return loader.get_source(environment, path)
            except TemplateNotFound:
                pass
        raise TemplateNotFound(template)


class App(object):
    request_class = Request
    response_class = Response

    def __init__(self, root_module, prefs=None, init_func=None):
        self.conf = self.get_prefs(prefs)
        self.root = self.get_root(root_module)

        self.modules = {'': self.root}
        self.modules.update(self.conf.modules._data)

        self.init()

    def init(self):
        self.init_modules()
        self.init_jinja()
        self.share_modules()

    @property
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
        prefs = self.default_prefs
        if prefs_:
            prefs_ = prefs_(self) if callable(prefs_) else prefs_
            prefs.update(prefs_)
        return DictByDot(prefs)

    def get_root(self, module):
        if not isinstance(module, Module):
            module = Module(module, self.conf.theme)
        return module

    def init_modules(self):
        for name, module in self.modules.items():
            if self.root == module:
                continue

            self.root.url_views.update(module.url_views)
            self.root.url_map.add(
                Submount('/%s' % name, module.url_rules)
            )

    def init_jinja(self):
        jinja_loaders = {}
        for name, module in self.modules.items():
            if not module.theme_path:
                continue
            prefix = name and '/%s' % name or name
            jinja_loaders[prefix] = FileSystemLoader(
                module.theme_path
            )
            self.root.add_route(
                '%s/<path:path>' % prefix,
                module.build_endpoint('tpl'),
                build_only=True
            )

        if jinja_loaders:
            self.jinja = Environment(loader=PrefixLoader(jinja_loaders))
            self.dispatch = SharedJinjaMiddleware(self.dispatch, self, '/')

    def share_modules(self):
        shares = {}
        for name, module in self.modules.items():
            if not module.theme_path:
                continue
            prefix = '%s%s' % (self.conf.theme.url_prefix, name)
            prefix = '%s' % prefix.rstrip('/')
            self.root.add_route(
                '%s/<path:path>' % prefix,
                module.build_endpoint(module.theme.endpoint),
                build_only=True
            )
            shares[prefix] = module.theme_path

        self.dispatch = SharedDataMiddleware(self.dispatch, shares)

    def url_for(self, endpoint, **values):
        prefix = endpoint.find(':')
        if prefix != -1:
            suffix = endpoint[prefix:]
            prefix = endpoint[0:prefix]
            if prefix in self.modules:
                module = self.modules[prefix]
                endpoint = '%s%s' % (module.import_name, suffix)
        return self.url_adapter.build(endpoint, values)

    def get_template(self, template):
        try:
            return self.jinja.get_template(template)
        except TemplateNotFound:
            return False
        except IOError:
            return False

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
