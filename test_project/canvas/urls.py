from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^test_url/$', 'canvas.views.test_url', name="test_url"),
    url(r'^test_model/(?P<model_id>\d+)/', 'canvas.views.test_model', name="test_model"),
    url(r'^test_signed_request/$', 'canvas.views.test_signed_request', name="test_signed_request"),
)
