from naya.testing import *

from examples import small


c = Client(small.app)


def test_app():
    go(c.get, 200, '/')
    app = c.app

    aye(True, hasattr(app, 'jinja'))

    aye('==', 1, len(app.modules))
    aye('in', '', app.modules)
    aye('==', app.modules[''], app.root)

    aye('==', 'examples.small.views', app.root.import_name)

    aye('==', '/', app.url_for(':hello'))
    aye('==', '/bob', app.url_for(':hello', name='bob'))
    aye('==', '/t/', app.url_for(':jinja', path=''))
    aye('==', '/t/index.html', app.url_for(':jinja', path='index.html'))
    aye('==', '/s/index.html', app.url_for(':theme', path='index.html'))


def test_urls():
    rv = go(c.get, 200, '/')
    aye('in', 'Hello world!', rv.data)

    rv = go(c.get, 200, '/t/index.html')
    aye('in', '/s/index.html', rv.data)

    rv = go(c.get, 200, '/s/index.html')
    aye('in', '{{ template }}', rv.data)

    go(c.get, 404, '/t/')
    go(c.get, 404, '/t/index')
    go(c.get, 404, '/t/not_found')
