from werkzeug import redirect, abort

from .testing import Client


class ShortcutMixin(object):
    def abort(self, *args, **kwargs):
        return abort(*args, **kwargs)

    def redirect(self, location, **kwargs):
        code = kwargs.pop('code', None)
        if kwargs:
            location = self.url_for(location, **kwargs)
        options = code and {'code': code} or {}
        return redirect(location, **options)

    def test_client(self, *args, **kwargs):
        url = kwargs.pop('url', '/')
        code = kwargs.pop('code', 200)

        client = Client(self, *args, **kwargs)
        client.get(url, code=code, chain_info=False)
        return client
