from naya import Module


root = Module(__name__)


@root.route('/hello', defaults={'name': 'World'})
@root.route('/hello/<name>')
def hello(app, name):
    return 'Hello %s!' % name
