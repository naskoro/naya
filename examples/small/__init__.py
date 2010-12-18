from naya.base import Naya

from . import views, blog


class App(Naya):
    import_name = __name__

    @Naya.marker.wrap_handler()
    def wrap_handler(self, handler):
        return handler

    @Naya.marker.config()
    def config(self):
        return {
            'debug': True,
            'testing': False,
            'modules': {'': views, 'blog': blog},
            'theme': {
                'path_suffix': '_static',
                'endpoint': 'static',
                'url_prefix': '/static'
            },
            'jinja': {
                'path_ends': ['index.html', '.html'],
                'path_allow': ['^(|index)$', '\.(css|js|html|txt)$'],
                'path_deny': ['^text\.txt$'],
                'theme_redirect': False,
            }
        }
