import mimetypes


class SharedJinjaMiddleware(object):
    def __init__(self, dispatch, app, prefix, context={}):
        self.dispatch = dispatch
        self.app = app
        self.prefix = prefix
        self.context = context

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '/')
        template = None
        if path.endswith('/'):
            path = '%sindex.html' % path
        if path.startswith(self.prefix):
            path = path[path.index(self.prefix):]
            path = '/%s' % path.lstrip('/')
            template = self.app.get_template(path)

        if not template:
            return self.dispatch(environ, start_response)

        guessed_type = mimetypes.guess_type(path)
        mime_type = guessed_type[0] or 'text/plain'

        context = {'app': self.app, 'template': path.lstrip('/')}
        context.update(self.context)

        template = template.render(context)

        response = self.app.response_class(template, mimetype=mime_type)
        return response(environ, start_response)
