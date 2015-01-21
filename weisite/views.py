from django.shortcuts import render
from django.http import HttpResponse, Http404
import datetime
import wei123.settings
from django.template import Template, Context
from django.template.loader import get_template
from django.shortcuts import render_to_response
from weisite.models import weixin_article
from weisite.weixinnetease import WeixinNetease

# Create your views here.
def home(request):
    articles = weixin_article.objects.all()
    return render_to_response('index.html', {'article_list' : articles})


def collect(request):
    netease = WeixinNetease()
    i = 0
    for article in netease.gather():
        weixin = weixin_article(post_title = article[0], \
            post_link = article[1], \
            post_user = article[2], \
            post_date = article[3])
        weixin.save()
        i += 1
    return HttpResponse('<a href="/wei/home">Back</a> Updated:%d' % (i))

def clean(request):
    weixin_article.objects.all().delete()
    return HttpResponse('<a href="/wei/home">Back</a> Cleaned')
