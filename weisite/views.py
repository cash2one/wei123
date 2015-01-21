from django.shortcuts import render
from django.http import HttpResponse, Http404
import datetime
import wei123.settings
from django.template import Template, Context
from django.template.loader import get_template
from django.shortcuts import render_to_response

# Create your views here.
def home(request):
    return render_to_response('index.html', {'name':'ming'})