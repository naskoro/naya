from naya import Module

from . import repos


mod = Module(__name__, {
    'maps': [(repos.map, '')]
})


@mod.route('/dashboard/')
def dashboard(app):
    return 'modular.front.dashboard'
