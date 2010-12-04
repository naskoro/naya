import os

from werkzeug import (
    SharedDataMiddleware, ClosingIterator,
    Response as BaseResponse, Request as BaseRequest
)
from werkzeug.exceptions import HTTPException
from werkzeug.routing import Map, Rule, Submount, BuildError

from .conf import Config
from .helpers import get_package_path, marker
from .session import SessionMixin
from .shortcut import ShortcutMixin


class UrlMap(object):
    def __init__(self, import_name):
        self.import_name = import_name
        self.url_map = Map()
        self.url_views = {}

    @property
    def url_rules(self):
        return self.url_map.iter_rules()

    def build_endpoint(self, endpoint):
        return '{0}.{1}'.format(self.import_name, endpoint)

    def add_route(self, rule, endpoint, view_func=None, **options):
        options['endpoint'] = endpoint
        self.url_map.add(Rule(rule, **options))
        if view_func:
            self.url_views[endpoint] = view_func

    def route(self, rule, **options):
        def decorator(func):
            endpoint = options.pop('endpoint', func.__name__)
            endpoint = self.build_endpoint(endpoint)
            self.add_route(rule, endpoint, func, **options)
            return func
        return decorator

    def add_map(self, map, prefix='', rule_factory=Submount):
        self.url_views.update(map.url_views)
        self.url_map.add(
            rule_factory('/%s' % prefix.rstrip('/'), map.url_rules)
        )


class BaseModule(UrlMap):
    def __init__(self, import_name, prefs=None):
        super(BaseModule, self).__init__(import_name)

        self.conf = self.get_prefs(prefs)
        self.root_path = get_package_path(self.import_name)

        theme_path = self.get_path(self.conf['theme:path_suffix'])
        self.theme_path = os.path.isdir(theme_path) and theme_path or None

        marker.init.run(self)

    def __call__(self, prefix, rule_factory=Submount):
        self.prefix = prefix
        self.rule_factory = rule_factory
        return self

    def reload(self):
        self.__init__(self.import_name, self.conf)

    @marker.defaults()
    def module_defaults(self):
        return {
            'theme': {
                'path_suffix': '_theme',
            },
            'maps': {}
        }

    @marker.init(0)
    def module_init(self):
        self.name = self.prefix = ''
        self.rule_factory = Submount

        self.maps = list(self.conf['maps'])
        for map in self.maps:
            self.add_map(*map)

    def get_prefs(self, prefs_):
        prefs = Config()
        marker.defaults.run(self, callback=lambda x: prefs.update(x))
        prefs.update(prefs_)
        return prefs

    def get_path(self, *args):
        args = list(args)
        args.insert(0, self.root_path)
        return os.path.join(*args)

    def __repr__(self):
        return '<naya.Module({0.import_name})>'.format(self)


class Response(BaseResponse):
    default_mimetype = 'text/html'


class Request(BaseRequest):
    pass


class BaseApp(BaseModule):
    request_class = Request
    response_class = Response

    @marker.defaults()
    def defaults(self):
        return {
            'debug': False,
            'theme': {
               'endpoint': 'theme',
               'url_prefix': '/s/'
            },
            'modules': {},
        }

    @marker.init(0)
    def init(self):
        self.modules = self.conf['modules']
        for name, module in self.modules.items():
            module.name = name
            self.add_map(module, module.prefix, module.rule_factory)

    @marker.init()
    def init_shares(self):
        shared = False
        endpoint = self.conf['theme:endpoint']
        url_prefix = self.conf['theme:url_prefix']

        modules = list(self.modules.values())
        modules.reverse()
        for module in modules:
            if not module.theme_path:
                continue
            prefix = '{0}/{1}'.format(
                url_prefix.rstrip('/'), module.prefix.lstrip('/')
            )
            self.share(module, prefix, endpoint)
            shared = True

        if shared or self.theme_path:
            self.share(self, url_prefix, endpoint)

    def share(self, module, prefix, endpoint):
        prefix = prefix.rstrip('/')
        self.add_route(
            '{0}/<path:path>'.format(prefix),
            module.build_endpoint(endpoint),
            build_only=True
        )
        if module.theme_path:
            self.dispatch = SharedDataMiddleware(
                self.dispatch, {prefix: module.theme_path}
            )

    def _endpoint(self, map, suffix):
        return '{0}.{1}'.format(map.import_name, suffix)

    def _url(self, endpoint, values):
        try:
            url = self.url_adapter.build(endpoint, values)
        except BuildError:
            url = None
        return url

    def url_for(self, endpoint, **values):
        prefix = endpoint.find(':')
        if prefix == -1:
            endpoint = endpoint
        else:
            suffix = endpoint[prefix + 1:]
            prefix = endpoint[0:prefix]
            url = None
            if prefix == '':
                url = self._url(self._endpoint(self, suffix), values)
                if url:
                    return url
            if not url and prefix in self.modules:
                url = self._url(
                    self._endpoint(self.modules[prefix], suffix), values
                )
                if url:
                    return url
            for map, prefix_ in self.maps:
                if prefix_ == prefix:
                    url = self._url(self._endpoint(map, suffix), values)
                    if url:
                        return url
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
        self.url_adapter = self.url_map.bind_to_environ(environ)

    def dispatch(self, environ, start_response):
        try:
            marker.pre_request.run(self)
            endpoint, values = self.url_adapter.match()
            handler = self.url_views[endpoint]
            response = handler(self, **values)
            response = self.make_response(response)
        except HTTPException, e:
            response = e
        response = self.make_response(response)

        marker.post_request.run(self, args=[response])
        return ClosingIterator(response(environ, start_response))

    def __call__(self, environ, start_response):
        self.pre_dispatch(environ)
        return self.dispatch(environ, start_response)


Module = BaseModule


class App(BaseApp, ShortcutMixin, SessionMixin):
    pass
