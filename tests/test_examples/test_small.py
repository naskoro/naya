from naya.helpers import marker
from naya.testing import aye, call, raises

from examples.small import App


app = App(prefs={
    'testing': True
})
c = app.test_client()


def test_app():
    aye('==', 'examples.small', app.import_name)
    aye('!=', False, app.jinja)

    aye('==', 5, call(len, marker.defaults.of(app)))
    aye('==', 4, call(len, marker.init.of(app)))
    aye('==', 2, call(len, app.modules))
    aye('==', 1, call(len, marker.pre_request.of(app)))
    aye('==', 1, call(len, marker.post_request.of(app)))
    aye('==', 1, call(len, marker.wrap_handler.of(app)))

    mod = app.modules['']
    aye('==', ('', ''), (mod['name'], mod['prefix']))
    aye('==', 'examples.small.views', mod.import_name)


def test_app_init():
    aye(True, app['testing'])
    aye(False, App()['testing'])

    App.import_name = None
    raises(AttributeError, lambda: App())


def test_url_for():
    aye('==', '/', app.url_for(':hello'))
    aye('==', '/bob', app.url_for(':hello', name='bob'))
    aye('==', '/t/', app.url_for(':jinja', path=''))
    aye('==', '/t/index.html', app.url_for(':jinja', path='index.html'))
    aye('==', '/static/index.html', app.url_for(':static', path='index.html'))

    aye('==', '/blog/', app.url_for(':blog.index'))
    aye('==', '/blog/', app.url_for('blog:index'))
    aye('==', '/blog/', app.url_for('examples.small.blog.index'))


def test_urls():
    c.get('/', code=200)
    aye('in', 'Hello world!', c.data)

    c.get('/t/index.html/', code=302)
    c.get('/t/index.html', code=302)
    c.get('/t/index', code=302)
    c.get('/t/index/', code=302)

    c.get('/t/index/', code=200, follow_redirects=True)
    aye('==', '/t/', c.path)
    aye('in', '/static/index.html', c.data)

    c.get('/static/main.css', code=200)
    aye('==', 'text/css', c.content_type)
    c.get('/static/main.js', code=200)
    aye('==', 'application/javascript', c.content_type)

    c.get('/static/index.html', code=200)
    aye('in', '{{ template }}', c.data)

    c.get('/blog/', code=200)
    aye('in', 'blog.index', c.data)

    c.get('/a/500', code=500)
    c.get('/a/403', code=403)
    c.get('/tuple/', code=201)

    c.get('/text/', code=200)
    c.get('/macro/', code=200)

    c.get('/r/', code=200, follow_redirects=True)
    aye('==', '/', c.path)

    c.get('/r/hello/', code=200, follow_redirects=True)
    aye('==', '/naspeh', c.path)

    e = raises(ValueError, c.get, '/wrong/', code=500)
    aye('==', e.args, ('View function did not return a response', ))

    c.get('/t/text.txt', code=404)
    c.get('/t/not_found', code=404)


def test_jinja_shared():
    app['jinja:path_deny'] = []
    c.get('/t/text.txt', code=200)
    c.get('/t/', code=200)

    app['jinja:path_deny'] = ['.*']
    c.get('/t/text.txt', code=404)
    c.get('/t/', code=404)

    app['jinja:theme_redirect'] = True
    c.get('/t/text.txt', code=302)
    c.get(c.path, code=200, follow_redirects=True)
    aye('==', '/static/text.txt', c.path)

    app['theme:url_prefix'] = '/t/'
    app.reload()
    c.get('/t/text.txt', code=200)

    app['jinja:path_allow'] = ['\.txt$']
    app['jinja:path_deny'] = []
    c.get('/t/text.txt', code=200)
    c.get('/t/', code=404)

    app['jinja:path_allow'] = ['.*']
    app['jinja:path_deny'] = ['\.html$']
    c.get('/t/text.txt', code=200)
    c.get('/t/', code=200)

    app['jinja:shared'] = False
    c.get('/t/', code=404)


def test_session():
    c.get('session/check/', code=200)
    aye('==', 'no answer', c.data)

    c.get('session/add/', code=200)
    aye('==', 'ok', c.data)

    c.get('session/check/', code=200)
    aye('==', 'answer is 42', c.data)

def test_testing():
    c.get('/')
    aye(True, hasattr(c, 'data'))
    aye(True, hasattr(c, 'content_type'))
    aye('==', 'text/html; charset=utf-8', c.content_type)
    aye(True, hasattr(c, 'status_code'))
    aye(True, 200, c.status_code)
    aye(True, hasattr(c, 'headers'))
    aye('in', ('Content-Length', '12'), c.headers.items())
    aye(True, hasattr(c, 'path'))
    aye('==', '/', c.path)
    aye(True, hasattr(c, 'url'))
    aye('==', 'http://localhost/', c.url)

    aye(False, hasattr(c, 'answer'))
