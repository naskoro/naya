from naya import App

from . import admin, front, blog


app = App(__name__, {
    'debug': True,
    'submodules': {
        'front': (front.mod, ''),
        'blog': (blog.mod, ''),
        'admin': admin.mod
    },
    'jinja': {
        'endpoint': 'tpl',
        'url_prefix': '/',
        'path_ends': ['.html', '/index.html']
    }
})
