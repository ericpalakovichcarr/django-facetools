from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^test_url/$', 'canvas.views.test_url', name="test_url"),
)
