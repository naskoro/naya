from naya.testing import *

from examples import small


c = Client(small.app)


def test_app():
    rv = go(c.get, 200, '/')
    aye('in', '/s/index.html', rv.data)
    app = c.app

    aye('==', True, hasattr(app, 'jinja'))

    aye('==', 1, len(app.modules))
    aye('in', '', app.modules)
    aye('==', app.modules[''], app.root)

    aye('==', 'examples.small.views', app.root.import_name)

    aye('==', '/hello/', app.url_for(':hello'))
    aye('==', '/hello/bob', app.url_for(':hello', name='bob'))
    aye('==', '/', app.url_for(':tpl', path='index.html'))
    aye('==', '/s/index.html', app.url_for(':theme', path='index.html'))
