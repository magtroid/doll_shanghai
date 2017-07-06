#!/usr/bin/env python
# coding=utf-8
'''Module for uqer login

Magtroid @ 2017-05-12 14:29
methods for uqer'''

import common

import cookielib
import requests
from lxml import etree

class UqerLogin(object):
    def __init__(self):
        self.headers = {
            'Referer': 'https://uqer.io/home/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
            'Host':'uqer.io',
        }
        self.session = requests.session()
        self.session.cookies = cookielib.LWPCookieJar(filename='uqer_cookie')

        self.logined_url = 'https://uqer.io/home/'
        self.post_url = 'https://gw.wmcloud.com/usermaster/authenticate/v1.json'
        # self.notebook_url = 'https://uqer.io/labs/notebooks/Notebook0.nb'
        self.notebook_url = 'https://uqer.io/labs/'

    def load_cookie(self):
        try:
            self.session.cookies.load(ignore_discard=True)
        except:
            print 'cookie failed'

    def post_param(self, account, password):
        print 'start to post param'
        post_data = {
                'username': account,
                'password': password,
                'rememberMe': 'false',
        }
        response = self.session.post(self.post_url, data=post_data, headers=self.headers)
        print 'end post param'
        self.session.cookies.save()

    def bool_login(self):
        self.load_cookie()
        response = self.session.get(self.logined_url, headers=self.headers)
        response.encoding='utf-8'
        selector = etree.HTML(response.text)
        common.print_net('uqer', response.text)

    def login(self, account, password):
        if not common.check_login(self.session, self.logined_url, self.headers):
            (account, password) = common.confirm_password(account, password)
            self.post_param(account, password);
            self.bool_login()
            common.check_login(self.session, self.logined_url, self.headers)

    def get_param(self):
        response = self.session.get(self.notebook_url, headers=self.headers)
        response.encoding='utf-8'
        # common.print_net('notebook', response.text)
