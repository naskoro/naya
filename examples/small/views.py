from naya import Module


mod = Module(__name__)


@mod.route('/', defaults={'name': 'world'})
@mod.route('/<name>')
def hello(app, name):
    return 'Hello %s!' % name


@mod.route('/wrong/')
def wrong(app):
    pass


@mod.route('/a/<int:code>')
def abort404(app, code):
    return app.abort(code)


@mod.route('/r/')
def redirect(app):
    return app.redirect('/')


@mod.route('/tuple/')
def tuple(app):
    return 'tuple', 201


@mod.route('/text/')
def text(app):
    return app.to_template('text.txt')


@mod.route('/macro/')
def macro(app):
    return app.from_template('text.txt', 'body')()


@mod.route('/session/add')
def session_add(app):
    app.session['answer'] = 42
    return 'ok'


@mod.route('/session/check')
def session_check(app):
    if 'answer' in app.session and app.session['answer'] == 42:
        return 'answer is 42'
    return 'no answer'
