from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^test_url/$', 'canvas.views.test_url', name="test_url"),
    url(r'^test_model/(?P<model_id>\d+)/', 'canvas.views.test_model', name="test_model")
)
