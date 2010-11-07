from naya.helpers import register
from naya.testing import *
from werkzeug.routing import BuildError

from examples import simple


c = Client(simple.app)


def test_app():
    rv = go(c.get, 200, '/')
    aye('==', 'Hello world!', rv.data)
    app = c.app

    aye('==', 'examples.simple', app.import_name)

    aye('len', 3, register.get(app, 'default_prefs'))
    aye('len', 3, register.get(app, 'init'))

    aye('==', False, app.jinja)

    aye('==', 1, len(app.modules))
    aye('==', app.modules[''], (app, ''))

    url_rules = list(app.url_rules)
    aye('==', 1, len(url_rules))
    aye('==', 'examples.simple:index', url_rules[0].endpoint)
    aye('==', '/', url_rules[0].rule)

    aye('==', '/', app.url_for(':index'))
    aye.raises(BuildError, lambda: app.url_for(':jinja', path='index.html'))
    aye.raises(BuildError, lambda: app.url_for(':theme', path='index.html'))
