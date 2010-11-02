from naya import Module


root = Module(__name__)


@root.route('/', defaults={'name': 'world'})
@root.route('/<name>')
def hello(app, name):
    return 'Hello %s!' % name
