import mimetypes
import os
import re

from jinja2 import (
    Environment, TemplateNotFound,
    PrefixLoader as PrefixLoaderBase, FileSystemLoader, ChoiceLoader
)
from werkzeug import redirect

from .helpers import marker


class JinjaModuleMixin(object):
    @marker.defaults()
    def jinja_module_defaults(self):
        return {
            'jinja': {
                'path_suffix': '_theme'
            }
        }

    @marker.init.index(1)
    def jinja_module_init(self):
        jinja_path = self.get_path(self['jinja:path_suffix'])
        self.jinja_path = os.path.isdir(jinja_path) and jinja_path or None


class JinjaMixin(object):
    @marker.defaults()
    def jinja_defaults(self):
        return {'jinja': {
            'shared': True,
            'endpoint': 'jinja',
            'url_prefix': '/t/',
            'path_ends': [],
            'path_allow': ['\.(css|js)$'],
            'path_deny': ['\.(png|jpg|ico|gif)$'],
            'default_mimetype': 'text/html',
            'theme_redirect': True,
            'prefix_separator': ':',
            'env': {
                'filters': {},
                'globals': {'app': self},
                'options': {'autoescape': True}
            }
        }}

    @marker.init()
    def jinja_init(self):
        self.jinja = False

        jinja_loaders = self.jinja_loaders()
        if not jinja_loaders:
            return

        self.jinja = Environment(
            loader=PrefixLoader(self, jinja_loaders),
            **self['jinja:env:options']
        )
        self.jinja.filters.update(self['jinja:env:filters'])
        self.jinja.globals.update(self['jinja:env:globals'])

        endpoint = self['jinja:endpoint']
        url_prefix = self['jinja:url_prefix']

        for module in [self] + self.modules.values():
            if not self.has_templates(module) and self != module:
                continue
            prefix = '%s%s' % (url_prefix, module['prefix'].lstrip('/'))
            self.add_route(
                '%s/<path:path>' % prefix.rstrip('/'),
                module.build_endpoint(endpoint),
                build_only=True
            )

        self.dispatch = SharedJinjaMiddleware(
            self.dispatch, self, url_prefix
        )

    def has_templates(self, module):
        return hasattr(module, 'jinja_path') and module.jinja_path

    def jinja_loaders(self):
        jinja_loaders = {}
        for module in [self] + self.modules.values():
            if not self.has_templates(module):
                continue
            prefix = module['prefix']
            prefix = prefix and '/%s' % prefix or prefix
            jinja_loaders.setdefault(prefix, [])
            jinja_loaders[prefix].append(FileSystemLoader(module.jinja_path))

        for prefix, loader in jinja_loaders.items():
            if isinstance(loader, list):
                jinja_loaders[prefix] = ChoiceLoader(loader)
        return jinja_loaders

    def to_template(self, template_name, **context):
        template = self.jinja.get_template(template_name)
        return template.render(**context)

    def from_template(self, template_name, attribute):
        return getattr(
            self.jinja.get_template(template_name).module, attribute
        )


class PrefixLoader(PrefixLoaderBase):
    def __init__(self, app, *args, **kwargs):
        self.app = app
        super(PrefixLoader, self).__init__(*args, **kwargs)

    def get_source(self, environment, template):
        prefix_separator = self.app['jinja:prefix_separator']
        for prefix, loader in self.mapping.items():
            path = template
            path = '/%s' % path.lstrip('/')
            if path.startswith(prefix):
                path = template[len(prefix):]
                if path.startswith(prefix_separator):
                    path = '/%s' % path[len(prefix_separator):]
                    loader.get_source(environment, path)
            try:
                return loader.get_source(environment, path)
            except TemplateNotFound:
                pass
        raise TemplateNotFound(template)


class SharedJinjaMiddleware(object):
    def __init__(self, dispatch, app, prefix, context={}):
        self.dispatch = dispatch
        self.app = app
        self.prefix = prefix
        self.context = context

    def is_allow_path(self, path):
        path = path.strip('/')
        for pattern in self.app['jinja:path_deny']:
            if re.search(pattern, path):
                return False
        for pattern in self.app['jinja:path_allow']:
            if re.search(pattern, path):
                return True
        return False

    def __call__(self, environ, start_response):
        conf = self.app.conf
        if not conf['jinja:shared']:
            return self.dispatch(environ, start_response)

        base_path = environ.get('PATH_INFO', '/')
        path_ends = conf['jinja:path_ends']
        template = None
        if base_path.startswith(self.prefix):
            path = base_path[len(self.prefix):]
            path = '/%s' % path.strip('/')
            path = path.rstrip('/')
            path_exists = path in self.app.jinja.list_templates()

            if not self.is_allow_path(path):
                if path_exists and conf['jinja:theme_redirect']:
                    path = self.app.url_for(
                        ':%s' % conf['theme:endpoint'],
                        path=path.lstrip('/')
                    )
                    if path != base_path:
                        return self.app.redirect(path)(environ, start_response)
                return self.dispatch(environ, start_response)

            paths = path_ends and [path + end for end in path_ends] or []
            paths = [path] + paths
            try:
                template = self.app.jinja.select_template(paths)
            except TemplateNotFound:
                template = None

        if not template:
            return self.dispatch(environ, start_response)

        real_path = template.name
        main_path = real_path
        for end in path_ends:
            pattern = '%s$' % re.escape(end)
            if re.search(pattern, real_path):
                path = re.sub(pattern, '/', real_path)
                if self.is_allow_path(path):
                    main_path = path
                    break

        main_path = main_path.lstrip('/')
        full_path = self.app.url_for(
            ':%s' % conf['jinja:endpoint'], path=main_path
        )
        if base_path != full_path:
            response = redirect(full_path)
            return response(environ, start_response)

        guessed_type = mimetypes.guess_type(real_path)
        mime_type = guessed_type[0] or conf['jinja:default_mimetype']

        real_path = real_path.lstrip('/')
        real_path = real_path.replace(conf['jinja:prefix_separator'], '/')

        context = {'template': real_path}
        context.update(self.context)

        template = template.render(context)

        response = self.app.response_class(template, mimetype=mime_type)
        return response(environ, start_response)
