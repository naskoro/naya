from naya import UrlMap


map = UrlMap(__name__)


@map.route('/repos/')
def list(app):
    return 'modular.front.repos.list'
