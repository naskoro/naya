from naya import App

from . import admin, front, blog


app = App(__name__, {
    'debug': True,
    'modules': {
        'front': front.mod(prefix=''),
        'blog': blog.mod(prefix=''),
        'admin': admin.mod(prefix='admin')
    },
    'jinja': {
        'endpoint': 'tpl',
        'url_prefix': '/',
        'path_ends': ['/index.html'],
        'path_allow': ['*.html'],
    }
})
