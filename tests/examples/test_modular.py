from naya.testing import aye

from examples.modular import app


c = app.test_client()


def test_app():
    aye('==', 'examples.modular', app.import_name)
    aye('!=', False, app.jinja)

    aye('len', 3, app.modules)

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
    c.get('/', code=200)

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
    c.get('/', code=200)
    aye('in', 'from front', c.data)

    c.get('/admin/', code=200)
    aye('in', 'text/html', c.content_type)
    aye('in', 'from admin', c.data)

    c.get('/admin/base.html', code=200)
    aye('in', 'front', c.data)

    c.get('/admin/base', code=302)
    c.get('/admin/base/', code=200)
    aye('in', 'text/html', c.content_type)
    aye('in', 'admin', c.data)

    c.get('/admin/test.html', code=200)
    aye('in', 'from front', c.data)

    c.get('/s/admin/base.html', code=200)
    aye('not in', 'admin', c.data)

    c.get('/s/admin/test.html', code=200)
    aye('not in', 'admin', c.data)

    c.get('/s/admin/index.html', code=200)
    aye('in', 'admin', c.data)

    c.get('/repos/', code=200)
    aye('in', 'modular.front.repos.list', c.data)

    c.get('/dashboard/', code=200)
    aye('in', 'modular.front.dashboard', c.data)

    c.get('/admin/dashboard', code=301)
    c.get(c.path, code=200, follow_redirects=True)
    aye('==', '/admin/dashboard/', c.path)
    aye('in', 'modular.admin.dashboard', c.data)

    c.get('/text.txt', code=404)
    c.get('/main.css', code=404)
    c.get('/admin/not_found', code=404)
    c.get('/admin/base/index', code=404)

def test_concrete_loader():
    def check(sep=':'):
        app.conf['jinja:prefix_separator'] = sep
        c.get('/admin%sbase.html' % sep, code=200)
        aye('in', 'admin', c.data)
        aye('in', '/s/admin/base.html', c.data)

    check()
    check('::')
    check('---')

