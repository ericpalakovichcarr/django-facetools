import os
import re
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
        if self.should_process_response(response):
            # Get the oauth url fandjango is redirecting the user to
            oauth_url = self.get_oauth_url(response.content, "window.parent.location =", ';')

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

    def should_process_response(self, response):
        # We're going to compare this response's content to Fandjango's template
        # for authorization and see if they are the same.  First we need to find
        # the dynamic content in the template and in this response's html
        try:
            oauth_url_to_remove = self.get_oauth_url(response.content, 'window.parent.location = ', ';')
        except:
            return False
        if response.content.count(oauth_url_to_remove) != 2:
            return False
        import fandjango
        template_path = os.path.join(os.path.dirname(fandjango.__file__), "templates/fandjango/authorize_application.html")
        with open(template_path) as fandjango_temlate_file:
            fandjango_template_content = fandjango_temlate_file.read()
        template_tags_to_remove = re.findall("\{\{.*url\|safe \}\}", fandjango_template_content)
        if len(template_tags_to_remove) != 2:
            return False

        # Strip out the dynamic content
        response_template_content = response.content.replace(oauth_url_to_remove, "")
        for template_tag_to_remove in template_tags_to_remove:
            fandjango_template_content = fandjango_template_content.replace(template_tag_to_remove, "")

        # If the response minus its dynamic content is identical to Fandjango's
        # template minus its dynamic content then we should process it
        return response_template_content == fandjango_template_content

    def get_oauth_url(self, content, start_token, end_token):
        start = content.index(start_token) + len(start_token)
        end = content.index(end_token, start)
        return content[start:end].strip()[1:-1] # remove any whitespace and quotes around the url