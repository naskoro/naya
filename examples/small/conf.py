from . import views

prefs = {
    'debug': True,
    'submodules': {'': views.mod},
    'theme': {
        'endpoint': 'static',
        'url_prefix': '/static'
    }
}
