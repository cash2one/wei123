from django.shortcuts import render
from django.http import HttpResponse, Http404
import datetime

# Create your views here.
def home(request):
    html = "<html><body>now is %s</body></html>" % (datetime.datetime.now())
    return HttpResponse(html)