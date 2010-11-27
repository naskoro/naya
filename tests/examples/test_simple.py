from naya.helpers import marker
from naya.testing import aye
from werkzeug.routing import BuildError

from examples.simple import app


c = app.test_client()


def test_app():

    aye('==', 'examples.simple', app.import_name)
    aye('==', ('', ''), (app.name, app.prefix))

    aye('==', False, app.jinja)
    aye('len', 4, marker.defaults.of(app))
    aye('len', 5, marker.init.of(app))
    aye('len', 0, app.modules)

    url_rules = list(app.url_rules)
    aye('len', 1, url_rules)
    aye('==', 'examples.simple.index', url_rules[0].endpoint)
    aye('==', '/', url_rules[0].rule)


def test_url_for():
    c.get('/', code=200)
    aye('==', 'Hello world!', c.data)

    aye('==', '/', app.url_for(':index'))
    aye.raises(BuildError, lambda: app.url_for(':jinja', path='index.html'))
    aye.raises(BuildError, lambda: app.url_for(':theme', path='index.html'))
