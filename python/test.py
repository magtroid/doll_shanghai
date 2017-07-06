#!/usr/bin/env python

import requests

headers = { 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.37',
        }

proxy = '111.155.116.200:8123'

proxies = {
        'https': 'https://' + proxy,
        'http': 'http://' + proxy,
}

session = requests.session()
try:
    response = session.get('https://bj.lianjia.com/chengjiao', headers=headers, proxies=proxies, timeout=10)
    # response = session.get('https://example.org', headers=headers, proxies=proxies, timeout=10)
    # print response.text
    print 'ok https'
except:
    try:
        # response = session.get('http://bj.lianjia.com/chengjiao/dongcheng', headers=headers, proxies=proxies, timeout=10)
        response = session.get('http://example.org', headers=headers, proxies=proxies, timeout=10)
        # print response.text
        print 'ok http'
    except:
        print 'fail'
