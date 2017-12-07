#!/usr/bin/env python
# coding=utf-8
'''For Zhihu login

Magtroid @ 2017-05-04 17:33
methods for zhihu
Not Finished yet'''

import common
import re
import requests
import sys
import urllib
try:
    import cookielib
except:
    import http.cookiejar as cookielib

class ZhihuLogin(object):
    '''Zhihu login class'''
    def __init__(self):
        self.headers = {
            'Host': 'www.zhihu.com',
            'Referer': 'https://www.zhihu.com/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
        }
        self.session = requests.session()
        self.session.cookies = cookielib.LWPCookieJar(filename='zhihu_cookie')
        self.url = 'https://www.zhihu.com'
        self.logined_url = 'https://www.zhihu.com/settings/profile'
        # try:
        #     session.cookies.load(ignore_discard=True)
        # except:
        #     print('error to load cookie')

    def get_xsrf(self):
        '''_xsrf is a dynamic parameter'''
        index_url = 'https://www.zhihu.com'
        # get _xsrf
        index_page = self.session.get(index_url, headers=self.headers)
        # html = index_page.text
        # print(html)

    def login(self, account, password):
        common.check_login(self.session, self.url, self.headers)
        (account, password) = common.confirm_password(account, password)
        # _xsrf = self.get_xsrf()
        if re.match(r'^1\d{10}$', account):
            print('phone number:')
            post_url = 'https://www.zhihu.com/login/phone_num'
            postdata = {
                    '_xsrf': '',
                    'password': password,
                    'phone_num': account,
            }
        else:
            if '@' in account:
                print('email:')
            else:
                print('illegal email address:')
                return 0
            post_url = 'https://www.zhihu.com/login/email'
            postdata = {
                '_xsrf': '',
                'password': password,
                'email': account
            }

        login_page = self.session.post(post_url, data=postdata, headers=self.headers)
