from datetime import datetime, timedelta

from werkzeug.contrib.securecookie import SecureCookie

from .helpers import marker


class SessionMixin(object):
    @marker.defaults()
    def session_defaults(self):
        return {'session': {
            'cookie_name': 'session',
            'secret_key': 'secret key',
            'permanent': True,
            'lifetime': timedelta(31)
        }}

    @marker.pre_request.index(0)
    def session_load(self):
        self.session = SecureCookie.load_cookie(
            self.request,
            self['session:cookie_name'],
            secret_key=self['session:secret_key']
        )

    @marker.post_request()
    def session_save(self):
        expires = None
        if self['session:permanent']:
            expires = datetime.utcnow() + self['session:lifetime']

        self.session.save_cookie(
            self.response,
            self['session:cookie_name'],
            expires=expires,
            httponly=True
        )
