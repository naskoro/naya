from naya.base import App

from . import views, blog


app = App(__name__, {
    'debug': True,
    'maps': [(blog.map, 'blog')],
    'modules': {'': views.mod},
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
