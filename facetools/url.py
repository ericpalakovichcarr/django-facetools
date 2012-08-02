from urlparse import urlparse

from django.http import HttpResponse
from django.shortcuts import redirect, render_to_response
from django.core.urlresolvers import reverse
from django.conf import settings
from django.template.context import RequestContext

def translate_url_to_facebook_url(url):
    """
    Converts a url on the canvas path to it's facebook equivalent.  Requires
    FACEBOOK_CANVAS_URL and FACEBOOK_CANVAS_PAGE to be set in your Django
    settings.

    ex: http://localhost:8000/canvas/page/ becomes https://apps.facebook.com/my_facebook_app/page/
    """
    url_parts = urlparse(url)
    canvas_url = settings.FACEBOOK_CANVAS_URL
    if canvas_url.endswith('/'): canvas_url = canvas_url[:-1]
    canvas_parts = urlparse(canvas_url)

    # Dont convert the url if its not a canvas url
    if url_parts.scheme and not canvas_url.startswith('%s://%s' % (url_parts.scheme, url_parts.netloc)):
        return url
    if url_parts.netloc and not (canvas_url.startswith('http://%s' % url_parts.netloc) or canvas_url.startswith('https://%s' % url_parts.netloc)):
        return url
    if url_parts.path and not url_parts.path.startswith('/'):
        net_loc = url_parts.path
        if '/' in net_loc: net_loc = net_loc[:net_loc.index('/')]
        if not (canvas_url.startswith('http://%s' % net_loc) or canvas_url.startswith('https://%s' % net_loc)):
            return url
    if not url_parts.path.startswith(canvas_parts.path):
        return url

    facebook_url = settings.FACEBOOK_CANVAS_PAGE
    if facebook_url.endswith('/'): facebook_url = facebook_url[:-1]
    start = len(url_parts.scheme) + len(url_parts.netloc)
    if url_parts.scheme.strip():
        start += len("://")
    start = url.index(canvas_parts.path, start) + len(canvas_parts.path)
    full_new_path = url[start:]
    return '%s%s' % (facebook_url, full_new_path)

def facebook_reverse(*args, **kwargs):
    """
    Drop in replacement for Django's reverse function.  Modifies
    the url so it accounts for the facebook canvas url::

        >>> reverse('myapp:page')
        /canvas/page/
        >>> facebook_reverse('myapp:page')
        https://apps.facebook.com/myapp/page/

    Refer to https://docs.djangoproject.com/en/1.3/topics/http/urls/#reverse
    for more information on the arguments ``facebook_reverse`` can take.
    """
    url = reverse(*args, **kwargs)
    return translate_url_to_facebook_url(url)

def facebook_redirect(to, skip_replace=False, request=None, *args, **kwargs):
    """
    Drop in replacement for Django's redirect function.  Instead of returning a
    redirect using HTTP status codes and header values, it returns a regular HTML
    response with an empty body and a javascript fragment that sets the
    location variable in the DOM:

        <script type="text/javascript">
            top.location.href="https://apps.facebook.com/myapp/page/";
        </script>

    This allows us to redirect inside a Facebook
    IFrame to outside facebook pages (like authentication) and causes the
    users url in the address bar to update when redirecting to another internal page.

    Uses a template defined at facetools/facebook_redirect.html.  If you'd like
    to provide your own template, override this template.  It'll be provided with a
    context variable `redirect_url` for the redirect url.  Set the `request` kwarg to a request
    if you'd like to have all your context processor values available in the template.

    Refer to https://docs.djangoproject.com/en/1.3/topics/http/shortcuts/#redirect
    for more information on the agruments the ``facebook_redirect`` can take.
    """
    redirect_response = redirect(to, *args, **kwargs)
    url = redirect_response['Location']
    if not skip_replace:
        url = translate_url_to_facebook_url(url)

    return render_to_response(
        "facetools/facebook_redirect.html",
        {'redirect_url':url},
        context_instance=RequestContext(request)
    )
