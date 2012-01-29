import urllib

from django.http import HttpResponseRedirect
from facetools.url import translate_url_to_facebook_url, facebook_redirect

GET_REDIRECT_PARAM = 'facebook_redirect'

class FacebookRedirectMiddleware():
    def process_request(self, request):
        # Look for GET parameter, and redirect if you find it
        redirect = request.GET.get(GET_REDIRECT_PARAM)
        if redirect:
            return facebook_redirect(redirect)
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
