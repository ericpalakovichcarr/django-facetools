import datetime
import time

from django.conf import settings
from django.test import TestCase

from facetools.common import parse_signed_request, create_signed_request, _create_permissions_string

try:
    from canvas.models import ModelForTests
except:
    pass

class CommonTests(TestCase):

    def test_create_permissions_string(self):
        permissions1 = ['read_stream','user_birthday','user_hometown']
        permissions2 = [' read_stream','user_birthday ',' user_hometown ']
        permissions3 = []
        permissions1 = _create_permissions_string(permissions1)
        permissions2 = _create_permissions_string(permissions2)
        permissions3 = _create_permissions_string(permissions3)
        self.assertEquals('read_stream,user_birthday,user_hometown', permissions1)
        self.assertEquals('read_stream,user_birthday,user_hometown', permissions2)
        self.assertEquals('', permissions3)

# -----------------------------------------------------------------------------
# Following code primarily by Reik Schatz. Taken from Fandjango. Thanks Reik!
# http://javasplitter.blogspot.com/
# https://github.com/reikje
# -----------------------------------------------------------------------------

class SignedRequestTests(TestCase):

    def setUp(self):
        self.old_secret = settings.FACEBOOK_APPLICATION_SECRET_KEY
        settings.FACEBOOK_APPLICATION_SECRET_KEY = "214e4cb484c28c35f18a70a3d735999b"

    def tearDown(self):
        settings.FACEBOOK_APPLICATION_SECRET_KEY = self.old_secret

    def test_parse_signed_request(self):
        TEST_SIGNED_REQUEST = 'm2i3DMpnOG3JxFiISuLPN5sTCe9d3NMRyq3pcAtpKd8=.eyJpc3N1ZWRfYXQiOiAxMzI2MDYzOTUwLCAib2F1dGhfdG9rZW4iOiAiQUFBQ2sydEM5ekJZQkFFanlRY0VKWkN0cjgxWkFMM0ZRRXdvcjI5N2lJdFhlRFFYYkZwY0t3ZmdlNjdBdHlYYnBaQld1Z2pEZGdSdmZwbzUyTlRJU0N0ajlpZjZzWkMzSmp0ZXJtMjVyeEhPUDUzMlpDM3BFWSIsICJ1c2VyX2lkIjogMTAwMDAzMzI2OTkwOTkzLCAiYWxnb3JpdGhtIjogIkhNQUMtU0hBMjU2In0='
        data = parse_signed_request(TEST_SIGNED_REQUEST, settings.FACEBOOK_APPLICATION_SECRET_KEY)

        self.assertEquals(data['user_id'], 100003326990993)
        self.assertEquals(data['algorithm'], 'HMAC-SHA256')
        self.assertEquals(data['oauth_token'], 'AAACk2tC9zBYBAEjyQcEJZCtr81ZAL3FQEwor297iItXeDQXbFpcKwfge67AtyXbpZBWugjDdgRvfpo52NTISCtj9if6sZC3Jjterm25rxHOP532ZC3pEY')
        self.assertEquals(data['issued_at'], 1326063950)

    def test_create_signed_request_only_user_id(self):
        signed_request_user = create_signed_request(settings.FACEBOOK_APPLICATION_SECRET_KEY, user_id=1, issued_at=1254459601, add_default_data=False)
        self.assertEquals(signed_request_user, 'Y0ZEAYY9tGklJimbbSGy2dgpYz9qZyVJp18zrI9xQY0=.eyJpc3N1ZWRfYXQiOiAxMjU0NDU5NjAxLCAidXNlcl9pZCI6IDEsICJhbGdvcml0aG0iOiAiSE1BQy1TSEEyNTYifQ==')

        data_user = parse_signed_request(signed_request_user, settings.FACEBOOK_APPLICATION_SECRET_KEY)
        self.assertEquals(sorted(data_user.keys()), sorted([u'user_id', u'algorithm', u'issued_at']))
        self.assertEquals(data_user['user_id'], 1)
        self.assertEquals(data_user['algorithm'], 'HMAC-SHA256')

    def test_create_signed_request_no_user_id(self):
        # Should end up as same signed request as above since user_id will default to 1
        signed_request_user = create_signed_request(settings.FACEBOOK_APPLICATION_SECRET_KEY, issued_at=1254459601, add_default_data=False)
        self.assertEquals(signed_request_user, 'Y0ZEAYY9tGklJimbbSGy2dgpYz9qZyVJp18zrI9xQY0=.eyJpc3N1ZWRfYXQiOiAxMjU0NDU5NjAxLCAidXNlcl9pZCI6IDEsICJhbGdvcml0aG0iOiAiSE1BQy1TSEEyNTYifQ==')

        data_user = parse_signed_request(signed_request_user, settings.FACEBOOK_APPLICATION_SECRET_KEY)
        self.assertEquals(sorted(data_user.keys()), sorted([u'user_id', u'algorithm', u'issued_at']))
        self.assertEquals(data_user['user_id'], 1)
        self.assertEquals(data_user['algorithm'], 'HMAC-SHA256')

    def test_create_signed_request_use_default_data(self):
        signed_request_user = create_signed_request(settings.FACEBOOK_APPLICATION_SECRET_KEY, user_id=490, issued_at=1254459601, add_default_data=True)
        data_user = parse_signed_request(signed_request_user, settings.FACEBOOK_APPLICATION_SECRET_KEY)
        self.assertEquals(data_user['user_id'], 490)
        self.assertEquals(data_user['algorithm'], 'HMAC-SHA256')
        self.assertEquals(data_user['issued_at'], 1254459601)
        self.assertEquals(data_user['expires'], 0)
        self.assertEquals(data_user['user']['country'], 'us')
        self.assertEquals(data_user['user']['locale'], 'en_US')
        self.assertEquals(data_user['user']['age']['min'], 0)
        self.assertEquals(data_user['user']['age']['max'], 150)

    def test_create_signed_request_all_data(self):
        today = datetime.datetime.now()
        tomorrow = today + datetime.timedelta(hours=1)

        signed_request_user = create_signed_request(
            app_secret = settings.FACEBOOK_APPLICATION_SECRET_KEY,
            user_id = '999',
            issued_at = 1254459600,
            expires = tomorrow,
            oauth_token = '181259711925270|1570a553ad6605705d1b7a5f.1-499729129|8XqMRhCWDKtpG-i_zRkHBDSsqqk',
            app_data = {},
            page = {
                'id': '1',
                'liked': True
            }, add_default_data=False
        )

        data_user = parse_signed_request(signed_request_user, settings.FACEBOOK_APPLICATION_SECRET_KEY)
        self.assertEquals(sorted(data_user.keys()), sorted([u'user_id', u'algorithm', u'issued_at', u'expires', u'oauth_token', u'app_data', u'page']))
        self.assertEquals(data_user['user_id'], '999')
        self.assertEquals(data_user['algorithm'], 'HMAC-SHA256')
        self.assertEquals(data_user['issued_at'], 1254459600)
        self.assertEquals(data_user['expires'], int(time.mktime(tomorrow.timetuple())))
        self.assertEquals(data_user['oauth_token'], '181259711925270|1570a553ad6605705d1b7a5f.1-499729129|8XqMRhCWDKtpG-i_zRkHBDSsqqk')
        self.assertEquals(data_user['app_data'], {})
        self.assertEquals(data_user['page'], {'id': '1','liked': True})

# ---------------------------------------------------------------------
# End snatched code by Reik Schatz.
# ---------------------------------------------------------------------