from werkzeug import redirect, abort

from .testing import Client


class ShortcutMixin(object):
    def abort(self, *args, **kwargs):
        return abort(*args, **kwargs)

    def redirect(self, *args, **kwargs):
        return redirect(*args, **kwargs)

    def test_client(self, *args, **kwargs):
        return Client(self, *args, **kwargs)
