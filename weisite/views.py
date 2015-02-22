from django.shortcuts import render
from django.http import HttpResponse, Http404
import datetime
import wei123.settings
import re
import base64
from django.template import Template, Context
from django.template.loader import get_template
from django.shortcuts import render_to_response
from weisite.models import weixin_article_info, weixin_poster, common_status
from weisite.weixinnetease import WeixinNetease
from weisite.weixin_netease_poster import WeixinNeteasePoster
from weisite.weixin_history import WeixinHistory
from weisite.weixin_poster import WeixinPoster

# Create your views here.
def home(request):
    articles = weixin_article_info.objects.all()
    return render_to_response('index.html', {'article_list' : articles})

def poster(request):
    posters = weixin_poster.objects.all().order_by('poster_id')
    return render_to_response('poster.html', {'poster_list' : posters})

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
    with open('/etc/hosts', 'r') as f:
        return HttpResponse(f.readlines())

def weixin_log(request):
    #out = ''
    action = request.REQUEST.get('action', 'default').upper()
    out = '<style>body{font-size:12px;font-family:Consolas;Georgia,Serif;} span{color:red;}</style>'
    out += 'Action:' + action + '    <a href="/weixin/home">Go Home</a><br>'
    if action == 'CLEAR':
        return HttpResponse(out)
        
    if action == 'GATHER':
        poster_id = request.REQUEST.get('poster', 'MjM5MDE0Mjc4MA==')
        user_id = 'MjI4OTg2NjU%3D'
        key = ''
        max_depth = 2
        
        session_pos = common_status.objects.filter(key='session')
        if session_pos:
            key = session_pos[0].value
            
        if key:
            app = WeixinHistory()
            info = app.gather(poster_id, user_id, key, max_depth)
            for item in info:
                out += '<a href="%s" target="_blank">%s</a><br>' % (item[5], item[4])
                
                poster = weixin_poster.objects.get(poster_id=item[7])  
                weixin_article_info(id=item[0],fileid=item[1],mid=item[2],datetime=item[3],title=item[4],content_url=item[5],cover_url=item[6],poster_id=poster,is_display=item[8]).save()
        else:
            out += 'empty key:' + key 
        return HttpResponse(out)
     
    if action == 'KEEP':
        session = request.REQUEST.get('session', '')
        common_status(key='session', value=session).save()
        out += 'session kept:%s complete' % (session)
        return HttpResponse(out)
        
    if action == 'ADDPOSTER':
        url = request.REQUEST.get('inputURL', '')
        if url:
            app = WeixinPoster()
            item = app.gather(url)
            weixin_poster(poster_id=item[0],poster_b64=item[1],poster_name=item[2],poster_last_thread=item[3]).save()
            out += 'poster name:%s<br>' % (item[2])
        out += 'poster added:%s<br>' % (url)
        return HttpResponse(out)
        
    out += '<a href="http://json-format.coding.io/" target="_blank">JSON Decodo Online</a><br><hr>'
    with open(wei123.settings.LOG_FILE, 'r') as f:
        for line in f.readlines():
            m = re.search('getmasssendmsg', line)
            if m:
                out += '<span>' + line + '</span><br>'
                paras = line[line.find('?')+1:]
                paras = paras[:paras.find(' ')]
                
                biz = ''
                uin = ''
                key = ''
                version = ''
                for keyval in paras.split('&'):
                    val = ''
                    vals = keyval.split('=')
                    
                    val = vals[1]
                    if vals[0] == '__biz':
                        vals[0] = 'biz'
                        val = keyval[keyval.find('=')+1:]
                        biz = val
                    if vals[0] == 'uin':
                        uin = val
                    if vals[0] == 'version':
                        version  = val
                    if vals[0] == 'key':
                        out += '<strong>%-10s:%s</strong>' % (vals[0], val) + '<br>'
                        key = val
                    else:
                        out += '<strong>%-10s</strong>:%s' % (vals[0], val) + '<br>'
                out += '<strong>[DEBUG]</strong><br>'
                out += '<a href="http://mp.weixin.qq.com/mp/getmasssendmsg?__biz=%s&uin=%s&key=%s&devicetype=android-17&version=%s&lang=zh_CN&count=10&f=json" target="_blank">LINK</a><br>' % (biz, uin, key, version)
                out += '<a href="/weixin/key?action=keep&session=%s">keep</a><br>' % (key)
                out += '<hr>'
    return HttpResponse(out)

def full_log(request):
    out = ''
    with open(LOG_FILE, 'r') as f:
        for line in f.readlines():
            out += line
    return HttpResponse(out)