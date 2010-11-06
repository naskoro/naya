from naya import App

from . import admin, front


def prefs():
    return {
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
    }

app = App(__name__, prefs())
