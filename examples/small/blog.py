from naya.helpers import marker


@marker.route('/')
def index(app):
    return 'blog.index'
