from naya.helpers import marker

from . import repos


@marker.defaults()
def defaults():
    return {
        'modules': {'': repos.mod}
    }


@marker.route('/dashboard/')
def dashboard(app):
    return 'modular.front.dashboard'
