# coding="utf-8"
#!/usr/bin/python

import poplib
import re
import urllib2
import sqlite3
from BeautifulSoup import BeautifulSoup

class WeixinNetease(object):
    """docstring for WeixinNetease"""
    def __init__(self):
        super(WeixinNetease, self).__init__()

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
                    weixin_link = mail_text
                    weixin_title = ''
                    weixin_date = ''
                    weixin_user = ''
                
                    soup = BeautifulSoup(urllib2.urlopen(mail_text).read())
                    node = soup.find('h2', attrs={'id':'activity-name'})
                    if node:
                        weixin_title = node.getText()
                    node = soup.find('em', attrs={'id':'post-date'})
                    if node:
                        weixin_date = node.getText()
                    node = soup.find('a', attrs={'id':'post-user'})
                    if node:
                        weixin_user = node.getText()
                    #print '%s link:%s date:%s user:%s' % (weixin_title, weixin_link, weixin_date, weixin_user)
                    weixin_info.append((weixin_title, weixin_link, weixin_user, weixin_date))

        return weixin_info, total_weixin

    def __save(self, weixin_info):
        if len(weixin_info) > 0:
            conn = sqlite3.connect('db.sqlite3')
            c = conn.cursor()
            c.executemany('insert into weisite_weixin_article(post_title, post_link, post_user, post_date) values (?,?,?,?)', weixin_info)
            conn.commit()
            conn.close()


if __name__ == '__main__':
    netease = WeixinNetease()
    for item in netease.gather():
        print item
