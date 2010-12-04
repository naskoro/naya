from naya.helpers import marker
from naya.testing import aye

from examples.small import app


c = app.test_client()


def test_app():
    aye('==', 'examples.small', app.import_name)
    aye('!=', False, app.jinja)

    aye('len', 5, marker.defaults.of(app))
    aye('len', 5, marker.init.of(app))
    aye('len', 1, app.modules)

    mod = app.modules['']
    aye('==', ('', ''), (mod.name, mod.prefix))
    aye('==', 'examples.small.views', mod.import_name)


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

    args = aye.raises(ValueError, c.get, '/wrong/', code=500)
    aye('==', args[0], 'View function did not return a response')

    c.get('/t/text.txt', code=404)
    c.get('/t/not_found', code=404)


def test_jinja_shared():
    app.conf['jinja:path_deny'] = []
    c.get('/t/text.txt', code=200)
    c.get('/t/', code=200)

    app.conf['jinja:path_deny'] = ['.*']
    c.get('/t/text.txt', code=404)
    c.get('/t/', code=404)

    app.conf['jinja:theme_redirect'] = True
    c.get('/t/text.txt', code=302)
    c.get(c.path, code=200, follow_redirects=True)
    aye('==', '/static/text.txt', c.path)

    app.conf['theme:url_prefix'] = '/t/'
    app.reload()
    c.get('/t/text.txt', code=200)

    app.conf['jinja:path_allow'] = ['\.txt$']
    app.conf['jinja:path_deny'] = []
    c.get('/t/text.txt', code=200)
    c.get('/t/', code=404)

    app.conf['jinja:path_allow'] = ['.*']
    app.conf['jinja:path_deny'] = ['\.html$']
    c.get('/t/text.txt', code=200)
    c.get('/t/', code=200)

    app.conf['jinja:shared'] = False
    c.get('/t/', code=404)


def test_session():
    c.get('session/check/', code=200)
    aye('==', 'no answer', c.data)

    c.get('session/add/', code=200)
    aye('==', 'ok', c.data)

    c.get('session/check/', code=200)
    aye('==', 'answer is 42', c.data)
