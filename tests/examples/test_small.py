from naya.testing import aye

from examples.small import app


c = app.test_client()


def test_app():
    aye('==', 'examples.small', app.import_name)
    aye('!=', False, app.jinja)

    aye('len', 1, app.modules)

    mod = app.modules['']
    aye('==', ('', ''), (mod.name, mod.prefix))
    aye('==', 'examples.small.views', mod.import_name)


def test_url_for():
    c.get('/', code=200)

    aye('==', '/', app.url_for(':hello'))
    aye('==', '/bob', app.url_for(':hello', name='bob'))
    aye('==', '/t/', app.url_for(':jinja', path=''))
    aye('==', '/t/index.html', app.url_for(':jinja', path='index.html'))
    aye('==', '/static/index.html', app.url_for(':static', path='index.html'))


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

    c.get('/static/index.html', code=200)
    aye('in', '{{ template }}', c.data)

    c.get('/t/index.txt', code=404)
    c.get('/t/not_found', code=404)
