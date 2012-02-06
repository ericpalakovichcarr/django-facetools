import urllib
import urlparse

from django.http import HttpResponseRedirect
from facetools.url import translate_url_to_facebook_url, facebook_redirect

GET_REDIRECT_PARAM = 'facebook_redirect'

class FacebookRedirectMiddleware(object):
    def process_request(self, request):
        # Look for GET parameter, and redirect if you find it
        redirect_url = request.GET.get(GET_REDIRECT_PARAM)
        if redirect_url:
            return facebook_redirect(redirect_url)
        return None

    def process_response(self, request, response):
        if type(response) == HttpResponseRedirect:
            facebook_url = translate_url_to_facebook_url(response['Location'])
            if facebook_url != response['Location']:
                get_params = urllib.urlencode({GET_REDIRECT_PARAM: facebook_url})
                prefix = "?"
                insert_position = len(response['Location'])
                if '?' in response['Location']:
                    prefix = "&"
                if "#" in response['Location']:
                    insert_position = response['Location'].index("#")
                response['Location'] = response['Location'][:insert_position] + \
                                       prefix + get_params + \
                                       response['Location'][insert_position:]
        return response

class FandjangoIntegrationMiddleware(object):
    def process_response(self, request, response):
        # Get the oauth url fandjango is redirecting the user to
        start_token = "window.parent.location ="
        start = response.content.index(start_token) + len(start_token)
        end = response.content.index(';', start)
        oauth_url = response.content[start:end].strip()[1:-1] # remove any whitespace and quotes around the url

        # Update the oauth url so that it's url it goes to after
        # the user authorizes the app is a translated facebook url
        redirect_uri = urlparse.parse_qs(urlparse.urlparse(oauth_url).query)['redirect_uri'][0]
        path = urlparse.urlparse(redirect_uri).path
        path = '/' + "/".join(path.split("/")[2:])
        if not path.endswith("/"): path = path + "/"
        new_url = translate_url_to_facebook_url(path)

        # Replace the old url with the new one
        start_token = "redirect_uri="
        start = oauth_url.index(start_token) + len(start_token)
        end = oauth_url.index("&", start)
        new_oauth_url = oauth_url.replace(oauth_url[start:end], urllib.quote_plus(new_url))
        response.content = response.content.replace(oauth_url, new_oauth_url)

        return response
