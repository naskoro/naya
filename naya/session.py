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

    @marker.pre_request()
    def session_load(self):
        self.session = SecureCookie.load_cookie(
            self.request,
            self.conf['session:cookie_name'],
            secret_key=self.conf['session:secret_key']
        )

    @marker.post_request()
    def session_save(self, response):
        expires = None
        if self.conf['session:permanent']:
            expires = datetime.utcnow() + self.conf['session:lifetime']

        self.session.save_cookie(
            response,
            self.conf['session:cookie_name'],
            expires=expires,
            httponly=True
        )
