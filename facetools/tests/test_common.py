import datetime
import time

from django.conf import settings
from django.test import TestCase
from facetools.urls import facebook_reverse, facebook_redirect
from fandjango.models import ModelForTests

from facetools.common import _parse_signed_request, _create_signed_request, _create_permissions_string

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

    def test_parse_signed_request(self):
        TEST_SIGNED_REQUEST = 'm2i3DMpnOG3JxFiISuLPN5sTCe9d3NMRyq3pcAtpKd8=.eyJpc3N1ZWRfYXQiOiAxMzI2MDYzOTUwLCAib2F1dGhfdG9rZW4iOiAiQUFBQ2sydEM5ekJZQkFFanlRY0VKWkN0cjgxWkFMM0ZRRXdvcjI5N2lJdFhlRFFYYkZwY0t3ZmdlNjdBdHlYYnBaQld1Z2pEZGdSdmZwbzUyTlRJU0N0ajlpZjZzWkMzSmp0ZXJtMjVyeEhPUDUzMlpDM3BFWSIsICJ1c2VyX2lkIjogMTAwMDAzMzI2OTkwOTkzLCAiYWxnb3JpdGhtIjogIkhNQUMtU0hBMjU2In0='
        data = _parse_signed_request(TEST_SIGNED_REQUEST, settings.FACEBOOK_APPLICATION_SECRET_KEY)

        self.assertEquals(data['user_id'], 100003326990993)
        self.assertEquals(data['algorithm'], 'HMAC-SHA256')
        self.assertEquals(data['oauth_token'], 'AAACk2tC9zBYBAEjyQcEJZCtr81ZAL3FQEwor297iItXeDQXbFpcKwfge67AtyXbpZBWugjDdgRvfpo52NTISCtj9if6sZC3Jjterm25rxHOP532ZC3pEY')
        self.assertEquals(data['issued_at'], 1326063950)

    def test_create_signed_request(self):
        # test sending only user_id
        signed_request_user_1 = _create_signed_request(settings.FACEBOOK_APPLICATION_SECRET_KEY, user_id=1, issued_at=1254459601)
        self.assertEquals(signed_request_user_1, 'Y0ZEAYY9tGklJimbbSGy2dgpYz9qZyVJp18zrI9xQY0=.eyJpc3N1ZWRfYXQiOiAxMjU0NDU5NjAxLCAidXNlcl9pZCI6IDEsICJhbGdvcml0aG0iOiAiSE1BQy1TSEEyNTYifQ==')

        data_user_1 = _parse_signed_request(signed_request_user_1, settings.FACEBOOK_APPLICATION_SECRET_KEY)
        self.assertEquals(sorted(data_user_1.keys()), sorted([u'user_id', u'algorithm', u'issued_at']))
        self.assertEquals(data_user_1['user_id'], 1)
        self.assertEquals(data_user_1['algorithm'], 'HMAC-SHA256')

        # test not sending a user_id which will default to user_id 1
        signed_request_user_2 = _create_signed_request(settings.FACEBOOK_APPLICATION_SECRET_KEY, issued_at=1254459601)
        self.assertEquals(signed_request_user_1, signed_request_user_2)

        # test sending each available named argument
        today = datetime.datetime.now()
        tomorrow = today + datetime.timedelta(hours=1)

        signed_request_user_3 = _create_signed_request(
            app_secret = settings.FACEBOOK_APPLICATION_SECRET_KEY,
            user_id = '999',
            issued_at = 1254459600,
            expires = tomorrow,
            oauth_token = '181259711925270|1570a553ad6605705d1b7a5f.1-499729129|8XqMRhCWDKtpG-i_zRkHBDSsqqk',
            app_data = {},
            page = {
                'id': '1',
                'liked': True
            }
        )

        data_user_3 = _parse_signed_request(signed_request_user_3, settings.FACEBOOK_APPLICATION_SECRET_KEY)
        self.assertEquals(sorted(data_user_3.keys()), sorted([u'user_id', u'algorithm', u'issued_at', u'expires', u'oauth_token', u'app_data', u'page']))
        self.assertEquals(data_user_3['user_id'], '999')
        self.assertEquals(data_user_3['algorithm'], 'HMAC-SHA256')
        self.assertEquals(data_user_3['issued_at'], 1254459600)
        self.assertEquals(data_user_3['expires'], int(time.mktime(tomorrow.timetuple())))
        self.assertEquals(data_user_3['oauth_token'], '181259711925270|1570a553ad6605705d1b7a5f.1-499729129|8XqMRhCWDKtpG-i_zRkHBDSsqqk')
        self.assertEquals(data_user_3['app_data'], {})
        self.assertEquals(data_user_3['page'], {'id': '1','liked': True})

# ---------------------------------------------------------------------
# End snatched code by Reik Schatz.
# ---------------------------------------------------------------------