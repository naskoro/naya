from naya import App

from . import views


app = App(__name__, {
    'debug': True,
    'submodules': {'': views.mod},
    'theme': {
        'endpoint': 'static',
        'url_prefix': '/static'
    }
})
