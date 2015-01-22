# coding="utf-8"
#!/usr/bin/python

import poplib
import re
import urllib2
import sqlite3
import json
from BeautifulSoup import BeautifulSoup

class WeixinHistory(object):
    """docstring for WeixinHistory"""
    def __init__(self):
        super(WeixinHistory, self).__init__()

    def gather(self, poster_id, user_id, key):

        url ='http://mp.weixin.qq.com/mp/getmasssendmsg?__biz=%s&uin=%s&key=%s&devicetype=android-17&version=2600023a&lang=zh_CN' \
        % (poster_id, user_id, key)

        print url

        headers = {'User-Agent':'MicroMessenger Client'}
        req = urllib2.Request(url, headers = headers)
        content = urllib2.urlopen(req)

        json_content = ''
        json_start = False
        json_end = False
        for line in content.read().split('\r\n'):
            print line
            m = re.search('msgList = .*', line)
            if m:
                json_start = True
                continue
            if json_start:
                print line
                json_content += line.strip()
            m = re.search(';', line)
            if json_start and m:
                json_end = True
                break

        print json_content



    def __save(self, weixin_info):
        if len(weixin_info) > 0:
            conn = sqlite3.connect('db.sqlite3')
            c = conn.cursor()
            c.executemany('insert into weisite_weixin_article(post_title, post_link, post_user, post_date) values (?,?,?,?)', weixin_info)
            conn.commit()
            conn.close()


if __name__ == '__main__':
    poster_id = 'MzA5MDM5MzgwOQ=='
    user_id = 'MjI4OTg2NjU%3D'
    key = '79cf83ea5128c3e5ed80bb731f2ce9d4a23cfd591722b7162eb31e84a99f5913f631ddf1758bed804bb9621340f2c746'

    app = WeixinHistory()
    app.gather(poster_id, user_id, key)
