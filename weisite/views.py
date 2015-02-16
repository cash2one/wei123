from django.shortcuts import render
from django.http import HttpResponse, Http404
import datetime
import wei123.settings
from django.template import Template, Context
from django.template.loader import get_template
from django.shortcuts import render_to_response
from weisite.models import weixin_article, weixin_poster, common_status
from weisite.weixinnetease import WeixinNetease
from weisite.weixin_netease_poster import WeixinNeteasePoster

# Create your views here.
def home(request):
    articles = weixin_article.objects.all().order_by('-id')
    return render_to_response('index.html', {'article_list' : articles})


def collect(request):
    netease_pos = common_status.objects.filter(key='netease_pos')
    start_pos = 1
    if netease_pos:
        start_pos = int(netease_pos[0].value)

    netease = WeixinNetease()
    i = 0
    articles, total_no = netease.gather(start_pos+1)
    for article in articles:
        weixin = weixin_article(post_title = article[0], \
            post_link = article[1], \
            post_user = article[2], \
            post_date = article[3])
        weixin.save()
        i += 1

    if netease_pos:
        netease_pos[0].value = str(total_no)
        netease_pos[0].save()
    else:
        if total_no > 0:
            common_status(key='netease_pos', value=str(total_no)).save()

    return HttpResponse('<a href="/weixin/home">Back</a> Updated:%d StartPos:%d Total Articles:%d' % (i, start_pos, total_no))

def clean(request):
    weixin_article.objects.all().delete()
    return HttpResponse('<a href="/weixin/home">Back</a> Cleaned')

def subscriber(request):
    app = WeixinNeteasePoster()
    posters, total = app.gather()
    for poster in posters:
        #print '%d,%s,%s,%d' % (poster)
        weixin_poster(poster_id = poster[0],poster_b64 = poster[1],poster_name = poster[2],poster_last_thread = poster[3]).save()
    return HttpResponse('<a href="/weixin/home">Back</a> Done')
    
def google(request):
    with open('\\etc\\hosts', 'r') as f:
        return HttpResponse(f.read())
