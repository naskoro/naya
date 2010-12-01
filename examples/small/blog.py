from naya import UrlMap


map = UrlMap(__name__)


@map.route('/')
def index(app):
    return 'blog.index'
