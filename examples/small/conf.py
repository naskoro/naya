from . import views

prefs = {
    'debug': True,
    'modules': {'': views.root},
    'theme': {
        'endpoint': 'static',
        'url_prefix': '/static'
    }
}
