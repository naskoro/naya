from naya import App

from . import views


app = App(__name__, {
    'debug': True,
    'modules': {'': views.mod},
    'theme': {
        'path_suffix': '_static',
        'endpoint': 'static',
        'url_prefix': '/static'
    },
    'jinja': {
        'path_ends': ['index.html', '.html'],
        'path_allow': ['*.css', '*.js', '*.html', '*.txt'],
        'path_deny': ['text.txt']
    }
})
