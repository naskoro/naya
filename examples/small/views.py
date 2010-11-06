from naya import Module


mod = Module(__name__)


@mod.route('/', defaults={'name': 'world'})
@mod.route('/<name>')
def hello(app, name):
    return 'Hello %s!' % name
