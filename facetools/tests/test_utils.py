import datetime
import time

from facetools.common import parse_signed_request, create_signed_request, _create_permissions_string
from facetools.tests.decorators import make_test_user
from django.conf import settings

def test_parse_signed_request():
    TEST_SIGNED_REQUEST = 'm2i3DMpnOG3JxFiISuLPN5sTCe9d3NMRyq3pcAtpKd8=.eyJpc3N1ZWRfYXQiOiAxMzI2MDYzOTUwLCAib2F1dGhfdG9rZW4iOiAiQUFBQ2sydEM5ekJZQkFFanlRY0VKWkN0cjgxWkFMM0ZRRXdvcjI5N2lJdFhlRFFYYkZwY0t3ZmdlNjdBdHlYYnBaQld1Z2pEZGdSdmZwbzUyTlRJU0N0ajlpZjZzWkMzSmp0ZXJtMjVyeEhPUDUzMlpDM3BFWSIsICJ1c2VyX2lkIjogMTAwMDAzMzI2OTkwOTkzLCAiYWxnb3JpdGhtIjogIkhNQUMtU0hBMjU2In0='
    data = parse_signed_request(TEST_SIGNED_REQUEST, settings.FACEBOOK_APPLICATION_SECRET_KEY)

    assert data['user_id'] == 100003326990993
    assert data['algorithm'] == 'HMAC-SHA256'
    assert data['oauth_token'] == 'AAACk2tC9zBYBAEjyQcEJZCtr81ZAL3FQEwor297iItXeDQXbFpcKwfge67AtyXbpZBWugjDdgRvfpo52NTISCtj9if6sZC3Jjterm25rxHOP532ZC3pEY'
    assert data['issued_at'] == 1326063950

def test_create_signed_request():
    # test sending only user_id
    signed_request_user_1 = create_signed_request(settings.FACEBOOK_APPLICATION_SECRET_KEY, user_id=1, issued_at=1254459601)
    assert signed_request_user_1 == 'Y0ZEAYY9tGklJimbbSGy2dgpYz9qZyVJp18zrI9xQY0=.eyJpc3N1ZWRfYXQiOiAxMjU0NDU5NjAxLCAidXNlcl9pZCI6IDEsICJhbGdvcml0aG0iOiAiSE1BQy1TSEEyNTYifQ=='

    data_user_1 = parse_signed_request(signed_request_user_1, settings.FACEBOOK_APPLICATION_SECRET_KEY)
    assert sorted(data_user_1.keys()) == sorted([u'user_id', u'algorithm', u'issued_at'])
    assert data_user_1['user_id'] == 1
    assert data_user_1['algorithm'] == 'HMAC-SHA256'

    # test not sending a user_id which will default to user_id 1
    signed_request_user_2 = create_signed_request(settings.FACEBOOK_APPLICATION_SECRET_KEY, issued_at=1254459601)
    assert signed_request_user_1 == signed_request_user_2

    # test sending each available named argument
    today = datetime.datetime.now()
    tomorrow = today + datetime.timedelta(hours=1)

    signed_request_user_3 = create_signed_request(
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

    data_user_3 = parse_signed_request(signed_request_user_3, settings.FACEBOOK_APPLICATION_SECRET_KEY)
    assert sorted(data_user_3.keys()) == sorted([u'user_id', u'algorithm', u'issued_at', u'expires', u'oauth_token', u'app_data', u'page'])
    assert data_user_3['user_id'] == '999'
    assert data_user_3['algorithm'] == 'HMAC-SHA256'
    assert data_user_3['issued_at'] == 1254459600
    assert data_user_3['expires'] == int(time.mktime(tomorrow.timetuple()))
    assert data_user_3['oauth_token'] == '181259711925270|1570a553ad6605705d1b7a5f.1-499729129|8XqMRhCWDKtpG-i_zRkHBDSsqqk'
    assert data_user_3['app_data'] == {}
    assert data_user_3['page'] == {
        'id': '1',
        'liked': True
    }

def test_create_permissions_string():
    permissions1 = ['read_stream','user_birthday','user_hometown']
    permissions2 = [' read_stream','user_birthday ',' user_hometown ']
    permissions3 = []
    permissions1 = _create_permissions_string(permissions1)
    permissions2 = _create_permissions_string(permissions2)
    permissions3 = _create_permissions_string(permissions3)
    assert 'read_stream,user_birthday,user_hometown' == permissions1
    assert 'read_stream,user_birthday,user_hometown' == permissions2
    assert '' == permissions3

def test_convert_url_to_facebook_url():
    from django.conf import settings
    from fandjango.utils import convert_url_to_facebook_url
    old_canvas_page = getattr(settings, 'FACEBOOK_CANVAS_PAGE', None)
    old_canvas_url = getattr(settings, 'FACEBOOK_CANVAS_URL', None)
    try:
        expected_url = "https://apps.facebook.com/fandjango-test/view/"

        # Test every combination of urls that could be set
        values = (
            ("https://apps.facebook.com/fandjango-test/", "https://apps.facebook.com/fandjango-test"),
            ("http://localhost:8000/canvas/", "http://localhost:8000/canvas"),
            ("/canvas/view/", "/canvas/view", "http://localhost:8000/canvas/view/", "http://localhost:8000/canvas/view")
        )
        for facebook_canvas_page in values[0]:
            for facebook_canvas_url in values[1]:
                for url_to_convert in values[2]:
                    settings.FACEBOOK_CANVAS_PAGE = facebook_canvas_page
                    settings.FACEBOOK_CANVAS_URL = facebook_canvas_url
                    assert expected_url == convert_url_to_facebook_url(url_to_convert)

        # Test that URLS outside of the canvas don't get converted
        url = "http://google.com"
        assert url == convert_url_to_facebook_url(url)
        url = "http://www.google.com"
        assert url == convert_url_to_facebook_url(url)
        url = "https://www.google.com"
        assert url == convert_url_to_facebook_url(url)
        url = "https://www.google.com/whateves"
        assert url == convert_url_to_facebook_url(url)
        url = "https://www.google.com/whateves/"
        assert url == convert_url_to_facebook_url(url)
        url = "https://google.com/whateves"
        assert url == convert_url_to_facebook_url(url)
        url = "https://google.com/whateves/"
        assert url == convert_url_to_facebook_url(url)
        url = "www.google.com"
        assert url == convert_url_to_facebook_url(url)
        url = "www.google.com/hey"
        assert url == convert_url_to_facebook_url(url)
        url = "google.com/yo"
        assert url == convert_url_to_facebook_url(url)
        url = "google.com/loud/noises/"
        assert url == convert_url_to_facebook_url(url)
        url = "/not_canvas/view"
        assert url == convert_url_to_facebook_url(url)
        url = "/not_canvas/view/"
        assert url == convert_url_to_facebook_url(url)
        url = "/canvas/view/"
        assert url != convert_url_to_facebook_url(url)

    finally:
        settings.FACEBOOK_CANVAS_PAGE = old_canvas_page
        settings.FACEBOOK_CANVAS_URL = old_canvas_url

from django.test import TestCase
from django.conf import settings
from fandjango.utils import facebook_reverse, facebook_redirect
from fandjango.models import ModelForTests

class FacebookReverseTests(TestCase):

    def setUp(self):
        self.old_canvas_page = getattr(settings, 'FACEBOOK_CANVAS_PAGE', None)
        self.old_canvas_url = getattr(settings, 'FACEBOOK_CANVAS_URL', None)
        settings.FACEBOOK_CANVAS_PAGE = "https://apps.facebook.com/fandjango-test"
        settings.FACEBOOK_CANVAS_URL = "https://localhost:8000/canvas/"

    def tearDown(self):
        settings.FACEBOOK_CANVAS_PAGE = self.old_canvas_page
        settings.FACEBOOK_CANVAS_URL = self.old_canvas_url

    def test_view_name_reverse(self):
        url = facebook_reverse('fandjango:test_url')
        self.assertEquals('%s/test_url/' % settings.FACEBOOK_CANVAS_PAGE, url)

class FacebookRedirectTests(TestCase):

    def setUp(self):
        self.test_model = ModelForTests.objects.create()
        self.old_canvas_page = getattr(settings, 'FACEBOOK_CANVAS_PAGE', None)
        self.old_canvas_url = getattr(settings, 'FACEBOOK_CANVAS_PATH', None)
        settings.FACEBOOK_CANVAS_PAGE = "https://apps.facebook.com/fandjango-test"
        settings.FACEBOOK_CANVAS_URL = "http://localhost:8000/canvas/"

    def tearDown(self):
        self.test_model.delete()
        settings.FACEBOOK_CANVAS_PAGE = self.old_canvas_page
        settings.FACEBOOK_CANVAS_URL = self.old_canvas_url

    def test_full_url_redirect(self):
        response = facebook_redirect("http://www.google.com")
        self.assertEquals(response.status_code, 200)
        self.assertIn('http://www.google.com', response.content)

    def test_full_local_url_redirect(self):
        response = facebook_redirect('http://localhost:8000/canvas/test_url/')
        self.assertEquals(response.status_code, 200)
        self.assertIn('%s/test_url/' % settings.FACEBOOK_CANVAS_PAGE, response.content)

    def test_model_url_redirect(self):
        response = facebook_redirect(self.test_model)
        self.assertEquals(response.status_code, 200)
        self.assertIn('%s/test_model/%s/' % (settings.FACEBOOK_CANVAS_PAGE, self.test_model.id), response.content)

    def test_view_name_redirect(self):
        response = facebook_redirect('fandjango:test_url')
        self.assertEquals(response.status_code, 200)
        self.assertIn('%s/test_url/' % settings.FACEBOOK_CANVAS_PAGE, response.content)
