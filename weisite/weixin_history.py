# coding="utf-8"
#!/usr/bin/python

import poplib
import re
import urllib2
import sqlite3
import json
import datetime
import base64
from BeautifulSoup import BeautifulSoup

class WeixinHistory(object):
    """docstring for WeixinHistory"""
    def __init__(self):
        super(WeixinHistory, self).__init__()

        self.poster_id = 0
        self.poster_b64 = ''

    def gather(self, poster_id, user_id, key):

        self.poster_id = poster_id
        self.poster_b64 = base64.b64encode(str(self.poster_id))

        url ='http://mp.weixin.qq.com/mp/getmasssendmsg?__biz=%s&uin=%s&key=%s&devicetype=android-17&version=2600023a&lang=zh_CNcount=10&f=json' \
        % (self.poster_b64, user_id, key)

        # debug function
        print url

        headers = {'User-Agent':'MicroMessenger Client'}
        req = urllib2.Request(url, headers = headers)
        stream = urllib2.urlopen(req)
        #print stream.read()
        self.parse(stream)
        return
        
    def parse(self, stream):
        print stream.read()
        json_content = stream.read()
        print json_content
        json_obj = json.loads(json_content)

        for list_item in json_obj['list']:
            # not article, just common message
            if list_item.has_key('app_msg_ext_info'):
                pass
            else:
                continue

            comm_msg_info = list_item['comm_msg_info']
            app_msg_ext_info = list_item['app_msg_ext_info']
            app_msg_ext_info_is_multi = int(list_item['app_msg_ext_info']['is_multi'])

            yield (
                '%s_%s' % (comm_msg_info['id'], app_msg_ext_info['fileid']), \
                app_msg_ext_info['fileid'], \
                comm_msg_info['id'], \
                int(comm_msg_info['datetime']), \
                app_msg_ext_info['title'], \
                app_msg_ext_info['content_url'].replace("&amp;", "&").replace("\\/", "/"), \
                app_msg_ext_info['cover'].replace("&amp;", "&").replace("\\/", "/"), \
                self.poster_b64, \
                True)

            multi_app_msg_item_list = list_item['app_msg_ext_info']['multi_app_msg_item_list']
            if app_msg_ext_info_is_multi:
                for item in multi_app_msg_item_list:
                    yield (
                        '%s_%s' % (comm_msg_info['id'], item['fileid']), \
                        item['fileid'], \
                        comm_msg_info['id'], \
                        int(comm_msg_info['datetime']), \
                        item['title'], \
                        item['content_url'].replace("&amp;", "&").replace("\\/", "/"), \
                        item['cover'].replace("&amp;", "&").replace("\\/", "/"), \
                        self.poster_b64, \
                        True)


    def save(self, weixin_info):
        conn = sqlite3.connect('..\\db.sqlite3')
        c = conn.cursor()
        for item in weixin_info:
            try:
                c.execute('insert into weisite_weixin_article_info values (?,?,?,?,?,?,?,?,?)', item)
            except sqlite3.IntegrityError, e:
                pass
            
        conn.commit()
        conn.close()

# base64
# poster_id = 3090393809
# uid = 228986657
if __name__ == '__main__':
    poster_id = 1632475601
    user_id = 'MjI4OTg2NjU%3D'
    key = '79cf83ea5128c3e544bf88712dfb2956d2794c9c4d46e2fd160574d537279a067eaf5d42a77b4795bb3f752f92478c90'
    app = WeixinHistory()
    info = app.gather(poster_id, user_id, key)
    #info = app.parse(open('out.htm', 'r'))

    #app.save(info)
