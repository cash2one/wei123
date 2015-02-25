# coding="utf-8"
# !/usr/bin/python

import urllib2
import sqlite3
import json
import base64
import time

class WeixinHistory(object):
    '''
    Get weixin article list from weixin'account
    '''

    def __init__(self):
        super(WeixinHistory, self).__init__()

        self.poster_id = 0
        self.poster_b64 = ''


    def gather(self, poster_id, user_id, key, max_depth=1):
        '''
        :param poster_id: poster id integer not b64
        :param user_id: user_id in b64 string
        :param key: weixin session
        :return: the article tuples
        '''
        self.poster_id = int(base64.b64decode(poster_id))
        self.poster_b64 = poster_id
        self.user_id = user_id
        self.key = key

        url = 'http://mp.weixin.qq.com/mp/getmasssendmsg?__biz=%s&uin=%s&key=%s&devicetype=android-17&version=2600023a&lang=zh_CN&count=10&f=json' \
              % (self.poster_b64, self.user_id, self.key)
        #print url
        return self.parse_url(url, max_depth)
        

    def parse_url(self, urlparam, max_depth=1):
        '''
        ' return ret_code, and whole_msg_list
        '''
        is_continue = True
        url = urlparam
        whole_msg_list = []
        depth = 0

        while( (depth < max_depth) and is_continue):
            weixin_headers = {'User-Agent': 'MicroMessenger Client'}
            stream = urllib2.urlopen(urllib2.Request(url, headers=weixin_headers))
            ret_code, msg_list, is_continue = self.parse(stream)
            if ret_code == 0:
                if msg_list:
                    whole_msg_list += msg_list

                if is_continue:
                    url = 'http://mp.weixin.qq.com/mp/getmasssendmsg?__biz=%s&uin=%s&key=%s&devicetype=android-17&version=2600023a&lang=zh_CN&frommsgid=%d&count=10&f=json' \
                        % (self.poster_b64, self.user_id, self.key, msg_list[-1][2])
                    print url
                    time.sleep(1) #traffic control
                depth += 1
            else:
                # error todo log here
                break;
        return ret_code, whole_msg_list



    def parse(self, stream):
        '''
        ' return ret_code, msg_list, is_continue
        ' once ret_code = 0, others are meaningful.
        '''
        msg_list = []
        is_continue = False
        ret_code = 0

        json_content = stream.read()
        json_obj = json.loads(json_content)

        if int(json_obj['ret']) < 0:
            # -3 no session
            # -6 traffic control
            ret_code = int(json_obj['ret'])
            return ret_code, msg_list, is_continue

        if int(json_obj['is_continue']) == 1:
            is_continue = True

        msg_list_raw = json_obj['general_msg_list'].replace('\\\"', '\"')
        #print msg_list_raw
        msg_list_json_obj = json.loads(msg_list_raw)
        for list_item in msg_list_json_obj['list']:
            # not article, just common message
            if list_item.has_key('app_msg_ext_info'):
                pass
            else:
                continue

            comm_msg_info = list_item['comm_msg_info']
            app_msg_ext_info = list_item['app_msg_ext_info']

            msg_list.append((
                '%s_%s' % (comm_msg_info['id'], app_msg_ext_info['fileid']), \
                app_msg_ext_info['fileid'], \
                comm_msg_info['id'], \
                int(comm_msg_info['datetime']), \
                app_msg_ext_info['title'], \
                app_msg_ext_info['content_url'].replace("&amp;", "&").replace("\\/", "/"), \
                app_msg_ext_info['cover'].replace("&amp;", "&").replace("\\/", "/"), \
                self.poster_id, \
                True))

            multi_app_msg_item_list = list_item['app_msg_ext_info']['multi_app_msg_item_list']
            if len(multi_app_msg_item_list):
                for item in multi_app_msg_item_list:
                    msg_list.append((
                        '%s_%s' % (comm_msg_info['id'], item['fileid']), \
                        item['fileid'], \
                        comm_msg_info['id'], \
                        int(comm_msg_info['datetime']), \
                        item['title'], \
                        item['content_url'].replace("&amp;", "&").replace("\\/", "/"), \
                        item['cover'].replace("&amp;", "&").replace("\\/", "/"), \
                        self.poster_id, \
                        True))

        return ret_code, msg_list,is_continue
        


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
    poster_id = 'MjM5NDI3NjE0MQ=='
    user_id = 'MjI4OTg2NjU%3D'
    key = '8ea74966bf01cfb64dee1608d1207977f5b11c1ffc5742fc48802af9705e1f036ca5aeec74473c01590055047fcddf1d'
    max_depth = 1
    app = WeixinHistory()
    info = app.gather(poster_id, user_id, key, max_depth)
    for item in info:
        print item
    # info = app.parse(open('out.htm', 'r'))

    app.save(info)
