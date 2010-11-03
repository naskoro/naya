from naya import App

from . import admin, front


def prefs():
    return {
        'debug': True,
        'modules': {
            '': front.mod,
            'admin': admin.mod
        },
        'jinja': {
            'shared': True,
            'endpoint': 'jinja',
            'url_prefix': '/',
            'path_ends': ['.html', '/index.html']
        }
    }

app = App(prefs())
