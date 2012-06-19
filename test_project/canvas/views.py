from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.conf import settings

from facetools import parse_signed_request
from canvas.models import ModelForTests

def test_url(request):
    return HttpResponse("<html><body>Hey there.</body></html>")

def test_model(request, model_id):
    get_object_or_404(ModelForTests, pk=int(model_id))
    return HttpResponse("<html><body>Hi, %s</body></html>" % model_id)

def test_signed_request(request):
    return render_to_response("blank.html", {
        'signed_request': parse_signed_request(request.POST['signed_request'], settings.FACEBOOK_APPLICATION_SECRET_KEY)
    }, context_instance=RequestContext(request))