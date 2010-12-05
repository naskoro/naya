from naya.base import NayaBit


mod = NayaBit(__name__)


@mod.route('/repos/')
def list(app):
    return 'modular.front.repos.list'
