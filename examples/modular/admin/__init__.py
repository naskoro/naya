from naya.base import Module


mod = Module(__name__)


@mod.route('/dashboard/')
def dashboard(app):
    return 'modular.admin.dashboard'
