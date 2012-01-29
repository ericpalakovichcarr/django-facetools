import types

from django.template.defaulttags import URLNode, url
from django import template

from facetools.url import translate_url_to_facebook_url

register = template.Library()

def facebook_url(parser, token):
    """
    Works exactly like the default url tag, except the final url is replaced
    with its facebook canvas equivalent if it's in the canvas app.

    Refer to https://docs.djangoproject.com/en/1.3/ref/templates/builtins/#url
    for more information on how to use this tag.
    """

    # The {% url %} tag's function generates a URLNode.  The URLNode's render
    # function handles generating the proper url.  We're going to move the
    # the render method and replace it with a new render method.  The new
    # method will call the old one and then adjust the url before returning.
    URLNode_obj = url(parser, token)
    URLNode_obj.old_render = URLNode_obj.render
    URLNode_obj.render = types.MethodType(
        replacement_URLNode_render_method,
        URLNode_obj,
        URLNode)
    return URLNode_obj
facebook_url = register.tag(facebook_url)

def replacement_URLNode_render_method(self, context):
    """
    Replacement for the URLNode's render method.  It's monkey patched into
    a URLNode instance in the facebook_url tag.
    """
    # NOTE: Pretend this method exists inside the URLNode class (because when it's called it will be)
    url_str = self.old_render(context)
    if url_str:
        url_str = translate_url_to_facebook_url(url_str)
    return url_str
