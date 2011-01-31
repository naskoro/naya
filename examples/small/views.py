from naya.helpers import marker


@marker.route('/', defaults={'name': 'world'})
@marker.route('/<name>')
def hello(app, name):
    return 'Hello %s!' % name


@marker.route('/wrong/')
def wrong(app):
    pass


@marker.route('/a/<int:code>')
def abort404(app, code):
    return app.abort(code)


@marker.route('/r/')
def redirect(app):
    return app.redirect('/')


@marker.route('/r/hello/')
def redirect_to_hello(app):
    return app.redirect(app.url_for(':hello', name='naspeh'))


@marker.route('/tuple/')
def tuple(app):
    return 'tuple', 201


@marker.route('/text/')
def text(app):
    return app.to_template('text.txt')


@marker.route('/macro/')
def macro(app):
    return app.from_template('text.txt', 'body')()


@marker.route('/session/add/')
def session_add(app):
    app.session['answer'] = 42
    return 'ok'


@marker.route('/session/check/')
def session_check(app):
    if 'answer' in app.session and app.session['answer'] == 42:
        return 'answer is 42'
    return 'no answer'
