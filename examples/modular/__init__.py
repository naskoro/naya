from naya.base import Naya

from . import admin, front, blog


app = Naya(__name__, {
    'debug': True,
    'modules': {
        'front': (front, {'prefix': ''}),
        'admin': (admin, {'prefix': 'admin'}),
        'blog': blog.mod(prefix=''),
    },
    'jinja': {
        'endpoint': 'tpl',
        'url_prefix': '/',
        'path_ends': ['/index.html'],
        'path_allow': ['^[\/\w]*$', '\.html$'],
        'theme_redirect': False,
    }
})
