import os

from werkzeug import SharedDataMiddleware, ClosingIterator, Response, Request
from werkzeug.exceptions import HTTPException
from werkzeug.routing import Map, Rule, Submount, BuildError

from .conf import Config
from .helpers import package_path, marker
from .session import SessionMixin
from .shortcut import ShortcutMixin


class Mapper(object):
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


class NayaBit(Mapper):
    marker = marker
    import_name = None

    def __init__(self, import_name=None, prefs=None):
        if self.import_name is None:
            if import_name is None:
                raise AttributeError('"import_name" no define')
        else:
            import_name = self.import_name

        super(NayaBit, self).__init__(import_name)

        self.root_path = package_path(self.import_name)
        self.conf = self.get_prefs(prefs)

        theme_path = self.get_path(self['theme:path_suffix'])
        self.theme_path = os.path.isdir(theme_path) and theme_path or None

        marker.init.run(self)

    def __getitem__(self, name):
        return self.conf[name]

    def __setitem__(self, name, value):
        self.conf[name] = value

    def __call__(self, **prefs):
        self.conf.update(prefs)
        return self

    @property
    def module_class(self):
        return self.__class__

    def reload(self):
        self.__init__(self.import_name, self.conf)

    @marker.defaults()
    def module_defaults(self):
        return {
            'theme': {
                'path_suffix': '_theme',
            },
            'name': '',
            'prefix': '',
            'rule_factory': Submount,
            'modules': {}
        }

    @marker.init.index(0)
    def module_init(self):
        self.modules = Config()
        modules = self['modules']
        for name, module in modules.items():
            if not isinstance(module, NayaBit):
                module = self.from_pymodule(module, name)
            module['name'] = name
            self.modules[name] = module
            self.add_map(module, module['prefix'], module['rule_factory'])

    def from_pymodule(self, module, name):
        prefs = {}
        if isinstance(module, (tuple, list)):
            module, prefs = module
        prefix = prefs['prefix'] if 'prefix' in prefs else name
        prefs = self.get_prefs(prefs, module)
        rules = marker.route.of(module)
        module = self.module_class(module.__name__, prefs)
        module['prefix'] = prefix
        for rule, args, kwargs in rules:
            module.route(*args, **kwargs)(rule)
        return module

    def get_prefs(self, prefs_, obj=None):
        obj = obj and obj or self
        prefs = Config()
        for func, args, kwargs in marker.defaults.of(obj):
            prefs.update(func(*args, **kwargs))
        for func, args, kwargs in marker.config.of(obj):
            prefs.update(func(*args, **kwargs))
        prefs.update(prefs_)
        return prefs

    def get_path(self, *args):
        args = list(args)
        args.insert(0, self.root_path)
        return os.path.abspath(os.path.join(*args))

    def __repr__(self):
        return '<{0.__class__.__name__}({0.import_name})>'.format(self)


class NayaResponse(Response):
    default_mimetype = 'text/html'


class NayaRequest(Request):
    pass


class NayaBase(NayaBit):
    request_class = NayaRequest
    response_class = NayaResponse
    module_class = NayaBit

    @marker.defaults()
    def defaults(self):
        return {
            'debug': False,
            'theme': {
               'endpoint': 'theme',
               'url_prefix': '/s/'
            },
        }

    @marker.init()
    def init_shares(self):
        shared = False
        endpoint = self['theme:endpoint']
        url_prefix = self['theme:url_prefix']

        modules = list(self.modules.values())
        modules.reverse()
        for module in modules:
            if not module.theme_path:
                continue
            prefix = '{0}/{1}'.format(
                url_prefix.rstrip('/'), module['prefix'].lstrip('/')
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

    @marker.init.index(100)
    def init_dispatch(self):
        for func in marker.middleware.of(self):
            self.dispatch = func[0](self.dispatch)

    def pre_dispatch(self, environ):
        self.request = Request(environ)
        self.url_adapter = self.url_map.bind_to_environ(environ)
        for func in marker.pre_request.of(self):
            response = func[0]()
            if response:
                return response

    def dispatch(self, environ, start_response):
        try:
            endpoint, values = self.url_adapter.match()
            handler = self.url_views[endpoint]
            for func in marker.wrap_handler.of(self):
                handler = func[0](handler)
            response = handler(self, **values)
            response = self.make_response(response)
        except HTTPException, e:
            response = e
        response = self.make_response(response)
        marker.post_request.run(self, response)
        return ClosingIterator(response(environ, start_response))

    def __call__(self, environ, start_response):
        response = self.pre_dispatch(environ)
        if response:
            return response(environ, start_response)
        return self.dispatch(environ, start_response)


class Naya(NayaBase, ShortcutMixin, SessionMixin):
    pass
