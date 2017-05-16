#!/usr/bin/env python
# coding=utf-8

import common

import requests
import urllib
import urllib2
import sys
import re
from lxml import etree
try:
    import cookielib
except:
    import http.cookiejar as cookielib

class GithubLogin(object):
    def __init__(self):
        self.headers = {
            'Referer': 'https://github.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
            'Host':'github.com'
        }
        self.login_url = 'https://github.com/login'
        self.post_url = 'https://github.com/session'
        self.logined_url = 'https://github.com/settings/profile'

        self.session = requests.session()
        self.session.cookies = cookielib.LWPCookieJar(filename='github_cookie')

    def load_cookie(self):
        try:
            self.session.cookies.load(ignore_discard=True)
        except:
            print 'cookie failed'

    def get_param(self):
        print 'start to get param'
        response = self.session.get(self.login_url, headers=self.headers)
        selector = etree.HTML(response.text)
        field_one = selector.xpath('//div/input[2]/@value')
        print field_one
        print 'end get param'
        return field_one
        pass

    def post_param(self, usr_id, password):
        print 'start to post param'
        post_data = {
                'commit': 'Sign in',
                'utf8': '✓',
                'authenticity_token': self.get_param()[0],
                'login': usr_id,
                'password': password,
        }
        response = self.session.post(self.post_url, data=post_data, headers=self.headers)
        print 'end post param'
        self.session.cookies.save()

        pass

    def bool_login(self):
        self.load_cookie()
        response = self.session.get(self.logined_url, headers=self.headers)
        selector = etree.HTML(response.text)
        line = response.text.encode('utf-8')
        flag = selector.xpath('//div[@class="column two-thirds"]/dl/dt/label/text()')
        with open('net.txt', 'w') as fp:
            fp.writelines(line)
        print 'personal setting Profile include: %s' % flag
        pass

    def login(self, usr_id, password):
        common.check_login(self.session, self.logined_url, self.headers)
        (usr_id, password) = common.confirm_password(usr_id, password)
        self.post_param(usr_id, password)
        self.bool_login()
        common.check_login(self.session, self.logined_url, self.headers)
