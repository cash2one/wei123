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
from itertools import chain
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.
def home(request):
    # https://docs.djangoproject.com/en/1.7/topics/db/queries/
    # https://docs.djangoproject.com/en/1.7/ref/models/querysets/
    # select by poster
    #articles = weixin_article_info.objects.filter(poster_id_id=3090393809).order_by('-datetime')
    
    article_list = weixin_article_info.objects.select_related('weixin_poster').order_by('-datetime')
    paginator = Paginator(article_list, 25) # Show 25 contacts per page
    page = request.GET.get('page')
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    for article in articles:
        # change the datetime format
        article.datetime = datetime.datetime.fromtimestamp(article.datetime).strftime('%Y-%m-%d %H:%M:%S')
    return render_to_response('index.html', {'article_list' : articles})
    
def display(request):
    return HttpResponse('<a href="/weixin/home">Back</a> Cleaned')

def poster(request):
    posters = weixin_poster.objects.all().order_by('poster_id')
    return render_to_response('poster.html', {'poster_list' : posters})

def test(request):
    name = 'ming'
    return render_to_response('weixin.html', {'name' :  name})

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
        weixin_poster(poster_id = poster[0],poster_b64 = poster[1],poster_name = poster[2],poster_qrcode = poster[3], poster_last_thread = poster[4]).save()
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
            ret_code, info = app.gather(poster_id, user_id, key, max_depth)
            if ret_code == 0:
                for item in info:
                    out += '<a href="%s" target="_blank">%s</a><br>' % (item[5], item[4])
                    
                    poster = weixin_poster.objects.get(poster_id=item[7])  
                    weixin_article_info(id=item[0],fileid=item[1],mid=item[2],datetime=item[3],title=item[4],content_url=item[5],cover_url=item[6],poster_id=poster,is_display=item[8]).save()
            else:
                out += 'error code:%d<br>' % (ret_code)
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
        
    if action == 'REMOVE_ARTICLES':
        id = request.REQUEST.get('poster', '')
        if id:
            weixin_article_info.objects.filter(poster_id=int(id)).delete()
            out += 'articles deleted:%s<br>' % (id)
        out += 'articles delete info:%s<br>' % (id)
        return HttpResponse(out)
    
    if action == 'REMOVE_POSTER':
        id = request.REQUEST.get('poster', '')
        if id:
            weixin_poster.objects.filter(poster_id=int(id)).delete()
            out += 'poster deleted:%s<br>' % (id)
        out += 'poster delete info:%s<br>' % (id)
        return HttpResponse(out)
        
    if action == 'GETFILE':
        path = request.REQUEST.get('filename', '')
        if path:
            f = open(path, 'rb')
            data = f.read()
            f.close()
            response = HttpResponse(data,mimetype='application/octet-stream') 
            response['Content-Disposition'] = 'attachment; filename=%s' % path
            return response
        else:
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
