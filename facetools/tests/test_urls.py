from django.conf import settings
from django.test import TestCase
from facetools.urls import facebook_reverse, facebook_redirect
from fandjango.models import ModelForTests

from facetools.urls import convert_url_to_facebook_url

if settings.FACETOOLS_TEST_ENV:
    from mock_django.models import ModelForTests

    class UrlTests(TestCase):

        def setUp(self):
            self.old_canvas_page = getattr(settings, 'FACEBOOK_CANVAS_PAGE', None)
            self.old_canvas_url = getattr(settings, 'FACEBOOK_CANVAS_PATH', None)
            settings.FACEBOOK_CANVAS_PAGE = "https://apps.facebook.com/fandjango-test"
            settings.FACEBOOK_CANVAS_URL = "http://localhost:8000/canvas/"
            self.test_model = ModelForTests.objects.create()

        def tearDown(self):
            settings.FACEBOOK_CANVAS_PAGE = self.old_canvas_page
            settings.FACEBOOK_CANVAS_URL = self.old_canvas_url
            self.test_model.delete()

        def test_convert_url_to_facebook_url(self):
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
                        self.assertEquals(expected_url, convert_url_to_facebook_url(url_to_convert))

            # Test that URLS outside of the canvas don't get converted
            url = "http://google.com"
            self.assertEquals(url, convert_url_to_facebook_url(url))
            url = "http://www.google.com"
            self.assertEquals(url, convert_url_to_facebook_url(url))
            url = "https://www.google.com"
            self.assertEquals(url, convert_url_to_facebook_url(url))
            url = "https://www.google.com/whateves"
            self.assertEquals(url, convert_url_to_facebook_url(url))
            url = "https://www.google.com/whateves/"
            self.assertEquals(url, convert_url_to_facebook_url(url))
            url = "https://google.com/whateves"
            self.assertEquals(url, convert_url_to_facebook_url(url))
            url = "https://google.com/whateves/"
            self.assertEquals(url, convert_url_to_facebook_url(url))
            url = "www.google.com"
            self.assertEquals(url, convert_url_to_facebook_url(url))
            url = "www.google.com/hey"
            self.assertEquals(url, convert_url_to_facebook_url(url))
            url = "google.com/yo"
            self.assertEquals(url, convert_url_to_facebook_url(url))
            url = "google.com/loud/noises/"
            self.assertEquals(url, convert_url_to_facebook_url(url))
            url = "/not_canvas/view"
            self.assertEquals(url, convert_url_to_facebook_url(url))
            url = "/not_canvas/view/"
            self.assertEquals(url, convert_url_to_facebook_url(url))
            url = "/canvas/view/"
            self.assertNotEquals(url, convert_url_to_facebook_url(url))

        def test_view_name_reverse(self):
            url = facebook_reverse('fandjango:test_url')
            self.assertEquals('%s/test_url/' % settings.FACEBOOK_CANVAS_PAGE, url)

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
