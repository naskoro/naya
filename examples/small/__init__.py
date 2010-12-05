from naya.base import Naya

from . import views, blog


app = Naya(__name__, {
    'debug': True,
    'modules': {'': views, 'blog': blog},
    'theme': {
        'path_suffix': '_static',
        'endpoint': 'static',
        'url_prefix': '/static'
    },
    'jinja': {
        'path_ends': ['index.html', '.html'],
        'path_allow': ['', '*.css', '*.js', '*.html', '*.txt'],
        'path_deny': ['text.txt'],
        'theme_redirect': False,
    }
})
