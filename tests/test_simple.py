from naya.testing import *

from examples import simple


c = Client(simple.app)


def test_app():

    rv = go(c.get, 200, '/')
    aye('==', 'Hello world!', rv.data)

    app = c.app

    print app.root.url_map
    aye('==', False, hasattr(app, 'jinja'))
    aye('==', '/', app.url_for(':index'))
    aye(hasattr, app, 'modules')
    aye(hasattr, app, 'root')
    aye('==', 1, len(app.modules))
    aye('in', '', app.modules)
    aye('==', 'examples.simple', app.root.import_name)


