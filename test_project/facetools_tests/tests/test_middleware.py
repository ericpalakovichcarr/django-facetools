import urlparse

from django.test import TestCase
from django.conf import settings
from django.http import HttpResponseRedirect, HttpRequest

from facetools.middleware import FacebookRedirectMiddleware, FandjangoIntegrationMiddleware, GET_REDIRECT_PARAM
from fandjango.views import authorize_application

class FacebookRedirectMiddlewareTests(TestCase):

    def test_response_and_request(self):
        expected_results = [
            ("/canvas/view", "/view"),
            ("/canvas/view#fragment", "/view#fragment"),
            ("/canvas/view/", "/view/"),
            ("/canvas/view/#fragment", "/view/#fragment"),
            ("/canvas/view/?hi=hey", "/view/?hi=hey"),
            ("/canvas/view/?hi=hey#fragment", "/view/?hi=hey#fragment"),
            ("/canvas/view/?hi=hey&pow=1", "/view/?hi=hey&pow=1"),
            ("/canvas/view/?hi=hey&pow=1#fragment", "/view/?hi=hey&pow=1#fragment"),
            ("/canvas/view?hi=hey", "/view?hi=hey"),
            ("/canvas/view?hi=hey#fragment", "/view?hi=hey#fragment"),
            ("/canvas/view?hi=hey&pow=1", "/view?hi=hey&pow=1"),
            ("/canvas/view?hi=hey&pow=1#fragment", "/view?hi=hey&pow=1#fragment"),
            ("http://google.com", None),
            ("http://www.google.com", None),
            ("https://www.google.com", None),
            ("https://www.google.com/whateves", None),
            ("https://www.google.com/whateves/", None),
            ("https://google.com/whateves", None),
            ("https://google.com/whateves/", None),
            ("www.google.com", None),
            ("www.google.com/hey", None),
            ("google.com/yo", None),
            ("google.com/loud/noises/", None),
            ("/not_canvas/view", None),
            ("/not_canvas/view#fragment", None),
            ("/not_canvas/view/", None),
            ("/not_canvas/view/#fragment", None),
            ("/not_canvas/view/?hi=hey", None),
            ("/not_canvas/view/?hi=hey#fragment", None),
            ("/not_canvas/view/?hi=hey&pow=1", None),
            ("/not_canvas/view/?hi=hey&pow=1#fragment", None),
            ("/not_canvas/view?hi=hey", None),
            ("/not_canvas/view?hi=hey#fragment", None),
            ("/not_canvas/view?hi=hey&pow=1", None),
            ("/not_canvas/view?hi=hey&pow=1#fragment", None),
        ]

        middleware = FacebookRedirectMiddleware()
        for original_redirect,new_redirect in expected_results:
            mock_response = HttpResponseRedirect(original_redirect)
            new_response = middleware.process_response(None, mock_response)
            if new_redirect is None:
                self.assertEquals(original_redirect, new_response['Location'])
            else:
                new_redirect = settings.FACEBOOK_CANVAS_PAGE + new_redirect
                self.assertTrue("?" in new_response['Location'])
                query = urlparse.parse_qs(urlparse.urlparse(new_response['Location']).query)
                self.assertEquals(new_redirect, query[GET_REDIRECT_PARAM][0])

                # Now test the request handler
                mock_request = HttpRequest()
                mock_request.GET[GET_REDIRECT_PARAM] = query[GET_REDIRECT_PARAM][0]
                response = middleware.process_request(mock_request)
                self.assertIn('top.location.href="%s"' % query[GET_REDIRECT_PARAM][0], response.content)

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

    def get_redirect_uri(self, response, start_token, end_token):
        start = response.content.index(start_token) + len(start_token)
        end = response.content.index(end_token, start)
        oauth_url = response.content[start:end]
        query = urlparse.parse_qs(urlparse.urlparse(oauth_url).query)
        return query['redirect_uri'][0]