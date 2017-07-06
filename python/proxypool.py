#!/usr/bin/env python
# coding=utf-8

import re
import requests
import sys
import time
import datalib

class ProxyPool(object):
    def __init__(self):
        self.headers = { 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.37',
        }
        self.session = requests.session()
        self.proxy_list = datalib.DataLib('./datalib/proxy.lib')
        self.proxy_list.load_data()
        self.write_data()
        self.proxy_num = 0
        self.proxy = {'http':'',
                      'https':''}
        self.request_num = 0
        self.request_threshold = 100
        self.test_url = {'http': 'http://example.org',
                         'https': 'https://example.org',}

    def show_proxy(self):
        print 'current proxy is %s' % self.proxy

    def insert_data(self, lkey, proxy_data):
        self.proxy_list.insert_data(lkey, proxy_data)
        self.proxy_num += 1

    def set_threshold(self, num):
        self.reqest_threshold = num

    def set_proxy(self, proxy):
        self.proxy[proxy['type']] = '%s://%s:%s' % (proxy['type'], proxy['ip'], proxy['port'])

    def simple_try_proxy(self, proxy):
        proxy_tmp = self.proxy.copy()
        self.set_proxy(proxy)
        try:
            response = self.session.get(self.test_url[proxy['type']], headers=self.headers, proxies=self.proxy, timeout=5)
            self.proxy.update(proxy_tmp)
            type = sys.getfilesystemencoding()
            return response.text.decode('utf-8').encode(type)
        except:
            print 'bad proxy: %s:%s, change one' % (proxy['ip'], proxy['port'])
            self.proxy.update(proxy_tmp)
            return ''

    def try_proxy(self, proxy, url):
        proxy_tmp = self.proxy.copy()
        self.set_proxy(proxy)
        try:
            response = self.session.get(url, headers=self.headers, proxies=self.proxy, timeout=5)
            self.proxy.update(proxy_tmp)
            type = sys.getfilesystemencoding()
            return response.text.decode('utf-8').encode(type)
        except:
            print 'bad proxy: %s:%s, change one' % (proxy['ip'], proxy['port'])
            self.proxy.update(proxy_tmp)
            return ''

    def reset_proxy(self):
        print 'reset proxy'
        for url_type in self.proxy.keys():
            self.proxy[url_type] = ''
        for url_type in self.proxy_list.data_lib.keys():
            for ip in self.proxy_list.data_lib[url_type].keys():
                self.proxy_list.data_lib[url_type][ip]['status'] = 'alive'

    def get_url_type(self, url):
        type = re.search('^(.*?)://', url).group(1)
        return type

    def switch_proxy(self, url):
        url_type = self.get_url_type(url)
        response = ''
        if self.proxy_list.data_lib.has_key(url_type) and len(self.proxy_list.data_lib[url_type]) is not 0:
            proxy_list = self.proxy_list.data_lib[url_type]
            loop = 0
            while not response:
                loop += 1
                for ip in proxy_list.keys():
                    # not selected:
                    if not response:
                        if proxy_list[ip]['status'] == 'alive':
                            response = self.try_proxy(proxy_list[ip], url)
                            if response:
                                self.set_proxy(proxy_list[ip])
                                proxy_list[ip]['success'] = str(int(proxy_list[ip]['success']) + 1)
                                proxy_list[ip]['status'] = 'using'
                            else:
                                proxy_list[ip]['fail'] = str(int(proxy_list[ip]['fail']) + 1)
                                proxy_list[ip]['status'] = 'dead'
                        elif proxy_list[ip]['status'] == 'using':
                            proxy_list[ip]['status'] = 'dead'
                        elif proxy_list[ip]['status'] == 'dead':
                            if loop is 1:
                                proxy_list[ip]['status'] = 'retry'  # set retry for second loop
                            elif loop is 2:
                                continue
                        else:  # retry
                            if loop is 1:  # wait for second loop
                                continue
                            elif loop is 2:
                                response = self.try_proxy(proxy_list[ip], url)
                                if response:
                                    self.set_proxy(proxy_list[ip])
                                    proxy_list[ip]['success'] = str(int(proxy_list[ip]['success']) + 1)
                                    proxy_list[ip]['status'] = 'using'
                                else:
                                    proxy_list[ip]['fail'] = str(int(proxy_list[ip]['fail']) + 1)
                                    proxy_list[ip]['status'] = 'dead'
                    # selected
                    else:
                        if proxy_list[ip]['status'] == 'alive':
                            continue
                        elif proxy_list[ip]['status'] == 'using':
                            proxy_list[ip]['status'] = 'dead'
                        elif proxy_list[ip]['status'] == 'dead':
                            proxy_list[ip]['status'] = 'retry'  # set retry for second loop
                        else:  # retry
                            if loop is 1:
                                continue
                            elif loop is 2:
                                proxy_list[ip]['status'] = 'alive'  # set retry for second loop
                if loop is 2:
                    break
            if not response:
                print 'no proxy available'
                self.reset_proxy()
                return response
            else:
                print 'switch proxy success, switch to %s' % self.proxy[url_type]
                return response
        else:
            print 'bad url type: %s' % url_type
            self.reset_proxy()
            return response

    def get_page(self, url, *param):
        time.sleep(1)
        response = ''

        if len(param) > 0 and param[0] == 'test_read':
            name = re.sub('https?://', '',  url)
            name = re.sub('/', '-', name)
            name = 'urls/' + name
            with open(name) as fp_in:
                lines = fp_in.readlines()
                for line in lines:
                    response = response + line

        if self.request_num < self.request_threshold:
            try:
                response = self.session.get(url, headers=self.headers, proxies=self.proxy, timeout=5)
                type = sys.getfilesystemencoding()
                response = response.text.decode('utf-8').encode(type)
            except:
                print 'bad proxy, switch proxy'
                response = self.switch_proxy(url)
                self.request_num = 0
        else:
            response = self.switch_proxy(url)
            self.request_num = 0
        self.request_num += 1

        if len(param) > 0 and param[0] == 'test_write':
            name = re.sub('https?://', '',  url)
            name = re.sub('/', '-', name)
            name = 'urls/' + name
            with open(name, 'w') as fp_out:
                fp_out.writelines(response)

        return response

    def write_data(self):
        self.proxy_list.write_data_lib()
