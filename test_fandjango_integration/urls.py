from django.conf.urls.defaults import patterns, include

urlpatterns = patterns('',
    (r'^canvas/', include('canvas.urls', namespace="canvas", app_name="canvas")),
)
