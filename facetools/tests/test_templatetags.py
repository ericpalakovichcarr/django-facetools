from django.template.base import Template
from django.template.context import Context
from django.test import TestCase
from django.conf import settings

from fandjango.models import ModelForTests

class Tests_facebook_url(TestCase):

    def setUp(self):
        self.test_model = ModelForTests.objects.create()
        self.old_canvas_page = getattr(settings, 'FACEBOOK_CANVAS_PAGE', None)
        self.old_canvas_url = getattr(settings, 'FACEBOOK_CANVAS_URL', None)
        settings.FACEBOOK_CANVAS_PAGE = "https://apps.facebook.com/fandjango-test"
        settings.FACEBOOK_CANVAS_URL = "/canvas/"

    def tearDown(self):
        self.test_model.delete()
        settings.FACEBOOK_CANVAS_PAGE = self.old_canvas_page
        settings.FACEBOOK_CANVAS_URL = self.old_canvas_url

    def test_url_by_view_name(self):
        t = Template("{% load facetools %}{% facebook_url fandjango:test_url %}")
        content = t.render(Context())
        self.assertIn('%s/test_url/' % settings.FACEBOOK_CANVAS_PAGE, content)

    def test_url_by_view_name_with_args(self):
        t = Template("{% load facetools %}{% facebook_url fandjango:test_model " + str(self.test_model.id) + " %}")
        content = t.render(Context())
        self.assertIn('%s/test_model/%s/' % (settings.FACEBOOK_CANVAS_PAGE, self.test_model.id), content)

    def test_using_as_with_tag(self):
        t = Template("{% load facetools %}{% facebook_url fandjango:test_model model_id=" + str(self.test_model.id) + " %}")
        content = t.render(Context())
        self.assertIn('%s/test_model/%s/' % (settings.FACEBOOK_CANVAS_PAGE, self.test_model.id), content)
