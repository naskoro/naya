from naya.testing import *

from examples import modular


c = Client(modular.app)


def test_app():
    rv = go(c.get, 200, '/')
    aye('in', '/s/index.html', rv.data)

    app = c.app
    aye('==', True, hasattr(app, 'jinja'))

    aye('==', 2, len(app.modules))
    aye('in', '', app.modules)
    aye('in', 'admin', app.modules)
    aye('==', app.modules[''], app.root)
    aye('==', 'examples.modular.front', app.root.import_name)
    aye('==', 'examples.modular.admin', app.modules['admin'].import_name)

    aye('==', '/', app.url_for(':tpl', path='/'))
    aye('==', '/', app.url_for(':tpl', path='index.html'))
    aye('==', '/admin/', app.url_for(':tpl', path='admin/'))
    aye('==', '/admin/index.html',
        app.url_for(':tpl', path='admin/index.html')
    )
    aye('==', '/admin/base.html', app.url_for(':tpl', path='admin/base.html'))
    aye('==', '/s/index.html', app.url_for(':theme', path='index.html'))
    aye('==', '/s/admin/index.html',
        app.url_for(':theme', path='admin/index.html')
    )


def test_urls():
    rv = go(c.get, 200, '/')
    aye('in', 'front', rv.data)

    rv = go(c.get, 200, '/admin/')
    aye('in', 'admin', rv.data)

    rv = go(c.get, 200, '/admin/base.html')
    aye('in', 'front', rv.data)

    rv = go(c.get, 200, '/admin/test.html')
    aye('in', 'front', rv.data)

    rv = go(c.get, 200, '/s/admin/base.html')
    aye('not in', 'admin', rv.data)

    rv = go(c.get, 200, '/s/admin/test.html')
    aye('not in', 'admin', rv.data)

    rv = go(c.get, 200, '/s/admin/index.html')
    aye('in', 'admin', rv.data)
