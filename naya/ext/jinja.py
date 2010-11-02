import mimetypes

from jinja2 import (
    Environment, TemplateNotFound,
    PrefixLoader as PrefixLoaderBase, FileSystemLoader
)

from naya.helpers import register


class JinjaMixin(object):
    def get_template(self, template):
        try:
            return self.jinja.get_template(template)
        except TemplateNotFound:
            return False
        except IOError:
            return False

    @register('init')
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


class SharedJinjaMiddleware(object):
    def __init__(self, dispatch, app, prefix, context={}):
        self.dispatch = dispatch
        self.app = app
        self.prefix = prefix
        self.context = context

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '/')
        if path.startswith(self.prefix):
            path = path[path.index(self.prefix):]
            path = path.rstrip('/')
            paths = ['%s' % path, '%s/index.html' % path, '%s.html' % path]
            try:
                template = self.app.jinja.select_template(paths)
            except TemplateNotFound:
                template = None

        if not template:
            return self.dispatch(environ, start_response)

        path = template.name

        guessed_type = mimetypes.guess_type(path)
        mime_type = guessed_type[0] or 'text/plain'

        context = {'app': self.app, 'template': path.lstrip('/')}
        context.update(self.context)

        template = template.render(context)

        response = self.app.response_class(template, mimetype=mime_type)
        return response(environ, start_response)
