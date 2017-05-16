#!/usr/bin/env python
# coding=utf-8

import requests
import sys
import ssl
import urllib2

def confirm_password(account, password):
    while not account:
        print 'user id is empty, please input your id:'
        account = sys.stdin.readline().strip()
    while not password:
        print 'password is empty, please input your password:'
        password = sys.stdin.readline().strip()
    return (account, password)

def check_login(session, url, headers):
    login_code = session.get(url, headers=headers, allow_redirects=False).status_code
    if login_code == 200:
        print 'login success!'
        return True
    else:
        print 'login failed!'
        return False

def print_net(name, text):
    file_name = name + '_net.txt'
    type = sys.getfilesystemencoding()
    text = text.decode('utf-8').encode(type)
    with open(file_name, 'w') as fp:
        fp.writelines(text)
