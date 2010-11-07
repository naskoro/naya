from naya.testing import *

from examples import modular


c = Client(modular.app)


def test_app():
    go(c.get, 200, '/')
    app = c.app

    aye('==', 'examples.modular', app.import_name)
    aye('!=', False, app.jinja)

    aye('==', 4, len(app.modules), app.modules)
    aye('==', app, app.modules[''][0])

    front = app.modules['front'][0]
    admin = app.modules['admin'][0]
    aye('==', 'examples.modular.front', front.import_name)
    aye('==', 'examples.modular.admin', admin.import_name)
    aye('==', 'examples.modular.blog', app.modules['blog'][0].import_name)

    aye('==', 2, len(app.shares))
    aye('==', ('/admin', admin), app.shares[0])
    aye('==', ('/', front), app.shares[1])

    aye('==', '/', app.url_for(':tpl', path=''))
    aye('==', '/', app.url_for(':tpl', path='/'))
    aye('==', '/index.html', app.url_for(':tpl', path='index.html'))
    aye('==', '/admin/', app.url_for(':tpl', path='admin/'))
    aye('==', '/admin/index.html',
        app.url_for(':tpl', path='admin/index.html')
    )
    aye('==', '/admin/base.html',
        app.url_for(':tpl', path='admin/base.html')
    )
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

    rv = go(c.get, 200, '/admin/base')
    aye('in', 'text/html', rv.content_type)
    aye('in', 'admin/base.html', rv.data)

    rv = go(c.get, 200, '/admin/test')
    aye('in', 'text/html', rv.content_type)

    go(c.get, 404, '/admin/not_found')
