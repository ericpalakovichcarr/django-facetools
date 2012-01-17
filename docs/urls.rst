Keeping your URLs DRY in Facebook
*********************************

facetools.urls
==============

The urls module contains functions that mirror the
``django.core.urlresolvers.reverse`` and ``django.shortcuts.redirect``
functions.

.. autofunction:: facetools.urls.facebook_reverse

.. autofunction:: facetools.urls.facebook_redirect

facetools.templatetags.facetools
================================

The ``facebook_url`` template tag serves the same purpose as
the above function, but for the standard ``url`` Django template
tag.

.. autofunction:: facetools.templatetags.facetools.facebook_url

Examples
========

TODO: Make examples