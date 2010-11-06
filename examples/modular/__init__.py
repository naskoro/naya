from naya import App

from . import admin, front


app = App(__name__, {
    'debug': True,
    'submodules': {
        '': front.mod,
        'admin': admin.mod
    },
    'jinja': {
        'endpoint': 'tpl',
        'url_prefix': '/',
        'path_ends': ['.html', '/index.html']
    }
})
