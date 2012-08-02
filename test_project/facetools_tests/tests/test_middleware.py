import urlparse

from django.test import TestCase
from fandjango.views import authorize_application

from facetools.middleware import FandjangoIntegrationMiddleware, GET_REDIRECT_PARAM
from test_project.canvas.views import test_url

class FandjangoMiddlewareTests(TestCase):

    def test_authorization_redirect_fix(self):
        unaltered_redirect_uri = 'http://apps.facebook.com/django-facetools/canvas/test_url/'
        altered_redirect_uri = 'https://apps.facebook.com/django-facetools/test_url/'

        # Make sure our assumptions about the URL's location are correct
        response = authorize_application(None, redirect_uri=unaltered_redirect_uri)
        unaltered_js_url = self.get_redirect_uri(response, "window.parent.location =", ';')
        unaltered_href_url = self.get_redirect_uri(response, 'You must <a href="', '"')
        self.assertEquals(unaltered_redirect_uri, unaltered_js_url)
        self.assertEquals(unaltered_redirect_uri, unaltered_href_url)

        # Make sure the URL gets changed to the proper URL
        middleware = FandjangoIntegrationMiddleware()
        response = middleware.process_response(None, response)
        altered_js_url = self.get_redirect_uri(response, "window.parent.location =", ';')
        altered_href_url = self.get_redirect_uri(response, 'You must <a href="', '"')
        self.assertEquals(altered_redirect_uri, altered_js_url)
        self.assertEquals(altered_redirect_uri, altered_href_url)
        self.assertEquals(200, response.status_code)

    def test_authorization_redirect_only_triggers_on_fandjango_authorization_redirect(self):
        response = authorize_application(None, redirect_uri="http://apps.facebook.com/django-facetools/canvas/test_url/")
        before_content = response.content
        response = FandjangoIntegrationMiddleware().process_response(None, response)
        after_content = response.content
        self.assertNotEquals(before_content, after_content)

        response = test_url(None)
        before_content = response.content
        response = FandjangoIntegrationMiddleware().process_response(None, response)
        after_content = response.content
        self.assertEquals(before_content, after_content)

    def get_redirect_uri(self, response, start_token, end_token):
        start = response.content.index(start_token) + len(start_token)
        end = response.content.index(end_token, start)
        oauth_url = response.content[start:end]
        query = urlparse.parse_qs(urlparse.urlparse(oauth_url).query)
        return query['redirect_uri'][0]