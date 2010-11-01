from naya import App

from . import admin, front


def prefs(app):
    return {
        'debug': True,
        'modules': {
            'admin': admin.mod
        }
    }

app = App(front.mod, prefs)
