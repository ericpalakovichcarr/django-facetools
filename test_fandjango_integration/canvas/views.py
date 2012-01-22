from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

def test_url(request):
    return render_to_response(
        'test_url.html',
        {'facebook': request.facebook},
        context_instance = RequestContext(request)
    )