from naya.helpers import register
from naya.testing import *
from werkzeug.routing import BuildError

from examples import simple


c = Client(simple.app)


def test_app():
    rv = go(c.get, 200, '/')
    aye('==', 'Hello world!', rv.data)
    app = c.app

    prefs = app.default_prefs()
    prefs.update(app.jinja_prefs())
    prefs.update({'modules': {'': app.root}})
    aye('==', app.conf, prefs)

    init_funcs = register.get_funcs(app, 'init')
    aye('==', 3, len(init_funcs), init_funcs)

    aye(False, hasattr(app, 'jinja'))

    aye('==', 1, len(app.modules))
    aye('in', '', app.modules)
    aye('==', app.modules[''], app.root)

    aye('==', 'examples.simple', app.root.import_name)

    url_rules = list(app.root.url_rules)
    aye('==', 1, len(url_rules))
    aye('==', 'examples.simple:index', url_rules[0].endpoint)
    aye('==', '/', url_rules[0].rule)

    aye('==', '/', app.url_for(':index'))
    aye.raises(BuildError, lambda: app.url_for(':jinja', path='index.html'))
    aye.raises(BuildError, lambda: app.url_for(':theme', path='index.html'))

