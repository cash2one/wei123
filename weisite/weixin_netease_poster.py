# coding="utf-8"
#!/usr/bin/python

import poplib
import re
import urllib2
import sqlite3
from BeautifulSoup import BeautifulSoup
from weisite.weixin_poster import WeixinPoster

class WeixinNeteasePoster(object):
    """docstring for WeixinNeteasePoster"""
    def __init__(self):
        super(WeixinNeteasePoster, self).__init__()

    def gather(self, start_pos=1):
        mail_client = poplib.POP3('pop3.163.com')

        try:
            mail_client.user('jasonnk001@163.com')
            mail_client.pass_('www.com')
        except Exception, e:
            mail_client.close()
            raise e

        numMessages = len(mail_client.list()[1])

        weixin_info = []
        total_weixin = numMessages

        if start_pos < numMessages+1:
            for i in range(start_pos, numMessages+1):
                mail_from = ''
                mail_encoding = ''
                mail_text = ''
                mail_start = False
                mail_end = False

                for j in mail_client.top(i, 30)[1]:
                    m = re.search('^From: (.*)', j)
                    if m:
                        mail_from = m.group(1)
                    m = re.search('^Content-Transfer-Encoding: (.*)', j)
                    if m:
                        mail_encoding = m.group(1)
                        
                    m = re.search('_Part_', j)
                    if m and mail_start:
                        mail_end = True
                        break # only extract first part
                        
                    if mail_from == 'jasonnk@163.com' and mail_encoding == '7bit' and not mail_start:
                        mail_start = True
                        continue
                    
                    if not mail_end and mail_start and j.strip() != '':
                        mail_text += j
                           
                if mail_text != '' and re.search('mp.weixin.qq.com', mail_text):
                    poster = WeixinPoster()
                    weixin_info.append(poster.gather(mail_text))

        return weixin_info, total_weixin


if __name__ == '__main__':
    netease = WeixinNeteasePoster()
    
    weixin_info, total_weixin = netease.gather()
    for i in weixin_info:
        print i
