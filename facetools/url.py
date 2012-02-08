from urlparse import urlparse

from django.http import HttpResponse
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.conf import settings

def translate_url_to_facebook_url(url):
    """
    Converts a url on the canvas path to it's facebook equivalent.  Requires
    FACEBOOK_CANVAS_URL and FACEBOOK_CANVAS_PAGE to be set in your Django
    settings.

    ex: http://localhost:8000/canvas/page/ becomes https://apps.facebook.com/my_facebook_app/page/
    """
    url_parts = urlparse(url)
    canvas_parts = urlparse(settings.FACEBOOK_CANVAS_URL)

    # Dont convert the url if its not a canvas url
    if url_parts.scheme and not settings.FACEBOOK_CANVAS_URL.startswith('%s://%s' % (url_parts.scheme, url_parts.netloc)):
        return url
    if not url_parts.path.startswith(canvas_parts.path):
        return url

    facebook_url = settings.FACEBOOK_CANVAS_PAGE
    if facebook_url.endswith('/'): facebook_url = facebook_url[:-1]
    new_path = url_parts.path.replace(canvas_parts.path, '')
    if not new_path.startswith('/'): new_path = '/%s' % new_path
    full_new_path = url[url.index(new_path):]
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

def facebook_redirect(to, skip_replace=False, *args, **kwargs):
    """
    Drop in replacement for Django's redirect function.  Instead of returning a
    redirect using HTTP status codes and header values, it returns a regular HTML
    response with an empty body and a javascript fragment that sets the
    location variable in the DOM::

        <script type="text/javascript">
            top.location.href="https://apps.facebook.com/myapp/page/";
        </script>

    This allows us to redirect inside a Facebook
    IFrame to outside facebook pages (like authentication) and causes the
    users url in the address bar to update when redirecting to another internal page.

    Refer to https://docs.djangoproject.com/en/1.3/topics/http/shortcuts/#redirect
    for more information on the agruments the ``facebook_redirect`` can take.
    """
    html_template = """
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
            "http://www.w3.org/TR/html4/loose.dtd">
    <html>
    <head>
        <script type="text/javascript">
            top.location.href="%(url)s";
        </script>
    </head>
    <body>
        <noscript>
            Redirecting to <a href="%(url)s" target="_top">%(url)s</a>.  Please <a href="%(url)s" target="_top">click here</a> if you aren't redirected.
        </noscript>
    </body>
    </html>
    """

    redirect_response = redirect(to, *args, **kwargs)
    url = redirect_response['Location']
    if not skip_replace:
        url = translate_url_to_facebook_url(url)

    return HttpResponse(html_template % {'url':url}, status=303)
