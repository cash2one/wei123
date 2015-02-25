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

class WeixinPoster(object):
    """docstring for WeixinPoster"""
    def __init__(self):
        super(WeixinPoster, self).__init__()

    def gather(self, url):
        headers = {'User-Agent':'MicroMessenger Client'}
        req = urllib2.Request(url, headers = headers)
        content = urllib2.urlopen(req)

        weixin_id = 0
        weixin_b64 = ''

        m = re.search('__biz=(.*?)&', url)
        if m:
            weixin_id = int(base64.b64decode(m.group(1)))
            weixin_b64 = m.group(1)

        weixin_name = self.parse(content)
        
        return (weixin_id, weixin_b64, weixin_name, 1)

    def parse(self, stream):
        soup = BeautifulSoup(stream.read())
        with open('d:\\out.txt','w') as f:
            f.write(soup.prettify())
        node = soup.find('a', attrs={'id':'post-user'})
        if node:
            weixin_poster = node.getText()
        node = soup.find('img', attrs={'id':'js_pc_qr_code_img'})
        if node:
            print node
            #weixin_qrcode = node['src']
            #print weixin_qrcode
        return weixin_poster


    def save(self, weixin_user_info):
        conn = sqlite3.connect('..\\db.sqlite3')
        c = conn.cursor()
        try:
            c.execute('insert into weisite_weixin_poster values (?,?,?,?)', weixin_user_info)
        except sqlite3.IntegrityError, e:
            pass
        conn.commit()
        conn.close()

# base64
# poster_id = 3090393809
# uid = 228986657
if __name__ == '__main__':
    app = WeixinPoster()
    #app.gather(poster_id, user_id, key)
    info = app.gather('http://mp.weixin.qq.com/s?__biz=MjM5NDEyOTEwMg==&mid=202288942&idx=1&sn=40f80067e5c2dfca4c9dd5385359d02c&scene=4#wechat_redirect')
    app.save(info)
