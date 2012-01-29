from django.conf import settings
from django.test import TestCase
from django.template.base import Template
from django.template.context import Context

from facetools.url import facebook_reverse, facebook_redirect, translate_url_to_facebook_url
from canvas.models import ModelForTests

class UrlTests(TestCase):

    def setUp(self):
        self.old_canvas_page = getattr(settings, 'FACEBOOK_CANVAS_PAGE', None)
        self.old_canvas_url = getattr(settings, 'FACEBOOK_CANVAS_PATH', None)
        settings.FACEBOOK_CANVAS_PAGE = "https://apps.facebook.com/django-facetools"
        settings.FACEBOOK_CANVAS_URL = "http://localhost:8000/canvas/"
        self.test_model = ModelForTests.objects.create()

    def tearDown(self):
        settings.FACEBOOK_CANVAS_PAGE = self.old_canvas_page
        settings.FACEBOOK_CANVAS_URL = self.old_canvas_url
        self.test_model.delete()

    def assert_url_translations(self, expected_url, urls_to_convert):
        values = (
            ("https://apps.facebook.com/django-facetools/", "https://apps.facebook.com/django-facetools"),
            ("http://localhost:8000/canvas/", "http://localhost:8000/canvas")
        )
        for facebook_canvas_page in values[0]:
            for facebook_canvas_url in values[1]:
                for url_to_convert in urls_to_convert:
                    settings.FACEBOOK_CANVAS_PAGE = facebook_canvas_page
                    settings.FACEBOOK_CANVAS_URL = facebook_canvas_url
                    self.assertEquals(expected_url, translate_url_to_facebook_url(url_to_convert))

    def test_translate_url_to_facebook_url(self):
        # Test plain urls
        self.assert_url_translations(
            "https://apps.facebook.com/django-facetools/view/",
            ("/canvas/view/", "http://localhost:8000/canvas/view/")
        )
        self.assert_url_translations(
            "https://apps.facebook.com/django-facetools/view",
            ("/canvas/view", "http://localhost:8000/canvas/view")
        )
        # Test urls with get parameters
        self.assert_url_translations(
            "https://apps.facebook.com/django-facetools/view/?hi=hey&ho=peter",
            ("/canvas/view/?hi=hey&ho=peter", "http://localhost:8000/canvas/view/?hi=hey&ho=peter")
        )
        self.assert_url_translations(
            "https://apps.facebook.com/django-facetools/view?hi=hey&ho=peter",
            ("/canvas/view?hi=hey&ho=peter", "http://localhost:8000/canvas/view?hi=hey&ho=peter")
        )
        # Test urls with fragments
        self.assert_url_translations(
            "https://apps.facebook.com/django-facetools/view/#bells",
            ("/canvas/view/#bells", "http://localhost:8000/canvas/view/#bells")
        )
        self.assert_url_translations(
            "https://apps.facebook.com/django-facetools/view#bells",
            ("/canvas/view#bells", "http://localhost:8000/canvas/view#bells")
        )
        # Test urls with get parameters and fragments
        self.assert_url_translations(
            "https://apps.facebook.com/django-facetools/view/?hi=hey&ho=peter#bells",
            ("/canvas/view/?hi=hey&ho=peter#bells", "http://localhost:8000/canvas/view/?hi=hey&ho=peter#bells")
        )
        self.assert_url_translations(
            "https://apps.facebook.com/django-facetools/view?hi=hey&ho=peter#bells",
            ("/canvas/view?hi=hey&ho=peter#bells", "http://localhost:8000/canvas/view?hi=hey&ho=peter#bells")
        )

        # Test that URLS outside of the canvas don't get converted
        url = "http://google.com"
        self.assertEquals(url, translate_url_to_facebook_url(url))
        url = "http://www.google.com"
        self.assertEquals(url, translate_url_to_facebook_url(url))
        url = "https://www.google.com"
        self.assertEquals(url, translate_url_to_facebook_url(url))
        url = "https://www.google.com/whateves"
        self.assertEquals(url, translate_url_to_facebook_url(url))
        url = "https://www.google.com/whateves/"
        self.assertEquals(url, translate_url_to_facebook_url(url))
        url = "https://google.com/whateves"
        self.assertEquals(url, translate_url_to_facebook_url(url))
        url = "https://google.com/whateves/"
        self.assertEquals(url, translate_url_to_facebook_url(url))
        url = "www.google.com"
        self.assertEquals(url, translate_url_to_facebook_url(url))
        url = "www.google.com/hey"
        self.assertEquals(url, translate_url_to_facebook_url(url))
        url = "google.com/yo"
        self.assertEquals(url, translate_url_to_facebook_url(url))
        url = "google.com/loud/noises/"
        self.assertEquals(url, translate_url_to_facebook_url(url))
        url = "/not_canvas/view"
        self.assertEquals(url, translate_url_to_facebook_url(url))
        url = "/not_canvas/view/"
        self.assertEquals(url, translate_url_to_facebook_url(url))
        url = "/canvas/view/"
        self.assertNotEquals(url, translate_url_to_facebook_url(url))

    def test_view_name_reverse(self):
        url = facebook_reverse('canvas:test_url')
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
        response = facebook_redirect('canvas:test_url')
        self.assertEquals(response.status_code, 200)
        self.assertIn('%s/test_url/' % settings.FACEBOOK_CANVAS_PAGE, response.content)

class FacebookUrlTests(TestCase):

    def setUp(self):
        self.test_model = ModelForTests.objects.create()
        self.old_canvas_page = getattr(settings, 'FACEBOOK_CANVAS_PAGE', None)
        self.old_canvas_url = getattr(settings, 'FACEBOOK_CANVAS_URL', None)
        settings.FACEBOOK_CANVAS_PAGE = "https://apps.facebook.com/django-facetools"
        settings.FACEBOOK_CANVAS_URL = "/canvas/"

    def tearDown(self):
        self.test_model.delete()
        settings.FACEBOOK_CANVAS_PAGE = self.old_canvas_page
        settings.FACEBOOK_CANVAS_URL = self.old_canvas_url

    def test_url_by_view_name(self):
        t = Template("{% load facetools_tags %}{% facebook_url canvas:test_url %}")
        content = t.render(Context())
        self.assertIn('%s/test_url/' % settings.FACEBOOK_CANVAS_PAGE, content)

    def test_url_by_view_name_with_args(self):
        t = Template("{% load facetools_tags %}{% facebook_url canvas:test_model " + str(self.test_model.id) + " %}")
        content = t.render(Context())
        self.assertIn('%s/test_model/%s/' % (settings.FACEBOOK_CANVAS_PAGE, self.test_model.id), content)

    def test_using_as_with_tag(self):
        t = Template("{% load facetools_tags %}{% facebook_url canvas:test_model model_id=" + str(self.test_model.id) + " %}")
        content = t.render(Context())
        self.assertIn('%s/test_model/%s/' % (settings.FACEBOOK_CANVAS_PAGE, self.test_model.id), content)
