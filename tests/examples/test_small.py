from naya.testing import *

from examples import small


c = Client(small.app)


def test_app():
    go(c.get, 200, '/')
    app = c.app

    aye('!=', False, app.jinja)

    aye('len', 1, app.modules)
    aye('in', '', app.modules)
    aye('!=', app.modules[''], (app, ''))

    aye('==', 'examples.small', app.import_name)

    aye('==', '/', app.url_for(':hello'))
    aye('==', '/bob', app.url_for(':hello', name='bob'))
    aye('==', '/t/', app.url_for(':jinja', path=''))
    aye('==', '/t/index.html', app.url_for(':jinja', path='index.html'))
    aye('==', '/static/index.html', app.url_for(':static', path='index.html'))


def test_urls():
    rv = go(c.get, 200, '/')
    aye('in', 'Hello world!', rv.data)

    rv = go(c.get, 200, '/t/index.html')
    aye('in', '/static/index.html', rv.data)

    rv = go(c.get, 200, '/static/index.html')
    aye('in', '{{ template }}', rv.data)

    go(c.get, 404, '/t/')
    go(c.get, 404, '/t/index')
    go(c.get, 404, '/t/not_found')
