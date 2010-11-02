from naya.testing import *

from examples import simple


c = Client(simple.app)


def test_app():

    rv = go(c.get, 200, '/')
    aye('==', 'Hello world!', rv.data)

    app = c.app
    aye('==', 3, len(app.init_funcs), app.init_funcs)
    aye('==', False, hasattr(app, 'jinja'))

    aye('==', 1, len(app.modules))
    aye('in', '', app.modules)
    aye('==', app.modules[''], app.root)

    aye('==', 'examples.simple', app.root.import_name)

    aye('==', '/', app.url_for(':index'))

