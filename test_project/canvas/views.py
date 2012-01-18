from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from canvas.models import ModelForTests

def test_url(request):
    return HttpResponse("<html><body>Hey there.</body></html>")

def test_model(request, model_id):
    get_object_or_404(ModelForTests, pk=int(model_id))
    return HttpResponse("<html><body>Hi, %s</body></html>" % model_id)