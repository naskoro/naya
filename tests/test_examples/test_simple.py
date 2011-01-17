from naya.helpers import marker
from naya.testing import aye, call, raises
from werkzeug.routing import BuildError

from examples.simple import app


c = app.test_client()


def test_client():
    result = c.get('/', code=200, as_tuple=True)
    aye('in', 'PATH_INFO', result[0])
    aye(True, call(isinstance, result[1], app.response_class))


def test_app():
    aye('==', 'examples.simple', app.import_name)
    aye('==', ('', ''), (app['name'], app['prefix']))

    aye(False, call(hasattr, app, 'jinja'))

    aye('==', 3, call(len, marker.defaults.of(app)))
    aye('==', 3, call(len, marker.init.of(app)))
    aye('==', 1, call(len, marker.pre_request.of(app)))
    aye('==', 1, call(len, marker.post_request.of(app)))
    aye('==', 0, call(len, marker.wrap_handler.of(app)))
    aye('==', 0, call(len, marker.middleware.of(app)))

    aye('==', 0, call(len, app.modules))

    url_rules = list(app.url_rules)
    aye('==', 1, call(len, url_rules))
    aye('==', 'examples.simple.index', url_rules[0].endpoint)
    aye('==', '/', url_rules[0].rule)


def test_url_for():
    c.get('/', code=200)
    aye('==', 'Hello world!', c.data)

    aye('==', '/', app.url_for(':index'))
    raises(BuildError, lambda: app.url_for(':jinja', path='index.html'))
    raises(BuildError, lambda: app.url_for(':theme', path='index.html'))
