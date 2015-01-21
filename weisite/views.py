from django.shortcuts import render
from django.http import HttpResponse, Http404
import datetime
import wei123.settings
from django.template import Template, Context
from django.template.loader import get_template
from django.shortcuts import render_to_response
from weisite.models import weixin_article, common_status
from weisite.weixinnetease import WeixinNetease

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

    return HttpResponse('<a href="/wei/home">Back</a> Updated:%d StartPos:%d Total Articles:%d' % (i, start_pos, total_no))

def clean(request):
    weixin_article.objects.all().delete()
    return HttpResponse('<a href="/wei/home">Back</a> Cleaned')
