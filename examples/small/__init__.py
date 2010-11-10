from naya import App

from . import views


app = App(__name__, {
    'debug': True,
    'modules': {'': views.mod},
    'theme': {
        'endpoint': 'static',
        'url_prefix': '/static'
    },
    'jinja': {'path_ends': ['index.html', '.html']}
})
