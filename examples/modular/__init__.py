from naya import App

from . import admin, front


def prefs(app):
    return {
        'debug': True,
        'modules': {
            'admin': admin.mod
        },
        'jinja': {
            'shared': True,
            'endpoint': 'jinja',
            'url_prefix': '/',
            'path_ends': ['.html', '/index.html']
        }
    }

app = App(front.mod, prefs)
