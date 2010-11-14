import mimetypes
import re

from jinja2 import (
    Environment, TemplateNotFound,
    PrefixLoader as PrefixLoaderBase, FileSystemLoader, ChoiceLoader
)
from werkzeug import redirect

from naya.helpers import register


class JinjaMixin(object):
    @register('default_prefs')
    def jinja_prefs(self):
        return {
            'jinja': {
                'shared': True,
                'endpoint': 'jinja',
                'url_prefix': '/t/',
                'path_ends': [],
                'path_allow': ['*.css', '*.js'],
                'path_deny': [],
                'filters': {},
            }
        }

    @register('init')
    def jinja_init(self):
        self.jinja = False

        jinja_loaders = self.jinja_loaders()
        if not jinja_loaders:
            return

        self.jinja = Environment(loader=PrefixLoader(jinja_loaders))
        self.jinja.filters.update(self.conf['jinja:filters'])

        if not self.conf['jinja:shared']:
            return

        endpoint = self.conf['jinja:endpoint']
        url_prefix = self.conf['jinja:url_prefix']

        for module in [self] + self.modules.values():
            if not module.theme_path and self != module:
                continue
            prefix = '%s%s' % (url_prefix, module.prefix.lstrip('/'))
            self.add_route(
                '%s/<path:path>' % prefix.rstrip('/'),
                module.build_endpoint(endpoint),
                build_only=True
            )

        self.dispatch = SharedJinjaMiddleware(
            self.dispatch, self, url_prefix
        )

    def jinja_loaders(self):
        jinja_loaders = {}
        for module in [self] + self.modules.values():
            if not module.theme_path:
                continue
            prefix = module.prefix
            prefix = prefix and '/%s' % prefix or prefix
            jinja_loaders.setdefault(prefix, [])
            jinja_loaders[prefix].append(FileSystemLoader(
                module.theme_path
            ))

        for prefix, loader in jinja_loaders.items():
            if isinstance(loader, list):
                jinja_loaders[prefix] = ChoiceLoader(loader)
        return jinja_loaders

    def render_to(self, template_name, **context):
        context.setdefault('app', self)
        template = self.jinja.get_template(template_name)
        return template.render(**context)


class PrefixLoader(PrefixLoaderBase):
    def get_source(self, environment, template):
        for prefix, loader in self.mapping.items():
            path = template
            path = '/%s' % path.lstrip('/')
            if path.startswith(prefix):
                path = template[len(prefix):]
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
        def prepare(pattern):
            pattern = re.escape(pattern)
            pattern = pattern.replace(r'\*', '.*')
            return pattern

        path = path.lstrip('/')
        for pattern in self.app.conf['jinja:path_deny']:
            if re.match(prepare(pattern), path):
                return False
        for pattern in self.app.conf['jinja:path_allow']:
            if re.match(prepare(pattern), path):
                return True
        return False

    def __call__(self, environ, start_response):
        base_path = environ.get('PATH_INFO', '/')
        template = None
        if base_path.startswith(self.prefix):
            path = base_path[len(self.prefix):]
            path = '/%s' % path.strip('/')
            path = path.rstrip('/')

            path_ends = self.app.conf['jinja:path_ends']
            paths = path_ends and [path + end for end in path_ends] or []
            paths = [path] + paths

            try:
                template = self.app.jinja.select_template(paths)
            except TemplateNotFound:
                template = None

        if not template or not self.is_allow_path(template.name):
            return self.dispatch(environ, start_response)

        real_path = template.name
        main_path = real_path
        for end in path_ends:
            pattern = '%s$' % re.escape(end)
            if re.search(pattern, real_path):
                main_path = re.sub(pattern, '/', real_path)
                break

        main_path = main_path.lstrip('/')
        full_path = self.app.url_for(
                ':%s' % self.app.conf['jinja:endpoint'], path=main_path
            )
        if base_path != full_path:
            response = redirect(full_path)
            return response(environ, start_response)

        guessed_type = mimetypes.guess_type(real_path)
        mime_type = guessed_type[0] or 'text/plain'

        context = {'app': self.app, 'template': real_path.lstrip('/')}
        context.update(self.context)

        template = template.render(context)

        response = self.app.response_class(template, mimetype=mime_type)
        return response(environ, start_response)
