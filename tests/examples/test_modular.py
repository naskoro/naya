from naya.testing import *

from examples import modular


c = Client(modular.app)


def test_app():
    app = c.app

    aye('==', 'examples.modular', app.import_name)
    aye('!=', False, app.jinja)

    aye('==', 3, len(app.modules), app.modules)

    front = app.modules['front']
    blog = app.modules['blog']
    admin = app.modules['admin']

    aye('==', ('front', ''), (front.name, front.prefix))
    aye('==', ('blog', ''), (blog.name, blog.prefix))
    aye('==', ('admin', 'admin'), (admin.name, admin.prefix))

    aye('==', 'examples.modular.front', front.import_name)
    aye('==', 'examples.modular.blog', blog.import_name)
    aye('==', 'examples.modular.admin', admin.import_name)


def test_url_for():
    go(c.get, 200, '/')
    app = c.app

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

    aye('==', '/repos/', app.url_for('front:repos.list'))
    aye('==', '/dashboard/', app.url_for('front:dashboard'))
    aye('==', '/admin/dashboard/', app.url_for('admin:dashboard'))


def test_urls():
    rv = go(c.get, 200, '/')
    aye('in', 'from front', rv.data)

    rv = go(c.get, 200, '/admin/')
    aye('in', 'text/html', rv.content_type)
    aye('in', 'from admin', rv.data)

    rv = go(c.get, 200, '/admin/base.html')
    aye('in', 'front', rv.data)

    rv = go(c.get, 302, '/admin/base')
    rv = go(c.get, 200, '/admin/base/')
    aye('in', 'text/html', rv.content_type)
    aye('in', 'admin', rv.data)

    rv = go(c.get, 200, '/admin/test.html')
    aye('in', 'from front', rv.data)

    rv = go(c.get, 200, '/s/admin/base.html')
    aye('not in', 'admin', rv.data)

    rv = go(c.get, 200, '/s/admin/test.html')
    aye('not in', 'admin', rv.data)

    rv = go(c.get, 200, '/s/admin/index.html')
    aye('in', 'admin', rv.data)

    rv = go(c.get, 200, '/repos/')
    aye('in', 'modular.front.repos.list', rv.data)

    rv = go(c.get, 200, '/dashboard/')
    aye('in', 'modular.front.dashboard', rv.data)

    rv = go(c.get, 301, '/admin/dashboard')
    rv = go(c.get, 200, '/admin/dashboard', follow_redirects=True)
    aye('in', 'modular.admin.dashboard', rv.data)

    go(c.get, 404, '/admin/not_found')
    go(c.get, 404, '/admin/base/index')
