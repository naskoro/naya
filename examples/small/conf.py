def get_prefs(app):
    return {
        'debug': True,
        'jinja': {
            'shared': True,
            'endpoint': 'jinja',
            'url_prefix': '/t/'
        }
    }
