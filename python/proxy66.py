#!/usr/bin/env python
# coding=utf-8

import proxypool
import re
import requests
import sys
import tools

class Proxy(object):
    def __init__(self):
        self.url = 'http://www.66ip.cn'
        self.target_url = 'https://bj.lianjia.com/chengjiao'
        self.max_num = 200
        self.proxy_num = 0
        self.proxy_pool = proxypool.ProxyPool()

    def get_proxy_list_page(self):
        target_page = ''
        success = False
        page = self.proxy_pool.get_page(self.url)
        while not success:
            net_search = re.search(r'<ul class="textlarge22"(.*?)</ul>', page, re.S)
            if net_search:
                success = True
                net = net_search.group(1)
            else:
                page = self.proxy_pool.switch_proxy(self.url)
                if not page:
                    print 'error to scrap proxy targe page'
                    return target_page
        proxy_list = re.findall(r'<li.*?href="(.*?)".*?</li>', net, re.S)
        return proxy_list[1:]

    def simple_try_proxy(self, proxy):
        type = ''
        proxy['type'] = 'http'
        if self.proxy_pool.simple_try_proxy(proxy):
            type = 'http'
        if not type:
            type = 'https'
            if self.proxy_pool.simple_try_proxy(proxy):
                type = 'https'
        return type

    def get_page_num(self, url):
        page_num = 0
        page = self.proxy_pool.get_page(url)
        net_search = re.search(r'div class="mypage".*<a href=".*?">(\d+)</a>', page, re.S)
        if net_search:
            page_num = int(net_search.group(1))
        else:
            print 'error to scrap page number'
        return page_num

    def get_proxy_data(self, url):
        page = self.proxy_pool.get_page(url)
### for test
        # name = re.sub('http://', '', url)
        # name = re.sub('/', '-', name)
        # name = 'urls/' + name
        # # with open(name, 'w') as fp_out:
        # #     fp_out.writelines(page)

        # page = ''
        # with open(name) as fp_in:
        #     lines = fp_in.readlines()
        #     for line in lines:
        #         page = page + line

### end for test
        proxy_search = re.search(r'(<table width.*?</table>)', page, re.S)
        while not proxy_search:
            page = self.proxy_pool.switch_proxy(url)
            if not page:
                print 'no proxy for url'
                return
            proxy_search = re.search(r'(<table width.*?</table>)', page, re.S)
        proxy_search = proxy_search.group(1)
        proxy_list = re.findall(r'(<tr.*?</tr>)', proxy_search, re.S)[1:]
        count = 0
        for sproxy in proxy_list:
            count += 1
            proxy_unit = dict()
            pattern_list = re.findall(r'<td.*?>(.*?)</td>', sproxy, re.S)
            proxy_unit['ip'] = pattern_list[0]
            proxy_unit['port'] = pattern_list[1]
            proxy_unit['city'] = pattern_list[2]
            proxy_unit['anony'] = pattern_list[3]
            # TODO(magtroid): gb2312 encoding
            # if not proxy_unit['anony'] == '高匿代理':
            #     print 'not anony, change one'
            #     continue
            proxy_unit['time'] = pattern_list[4]
            proxy_unit['success'] = 0
            proxy_unit['fail'] = 0
            proxy_unit['status'] = 'alive'
            proxy_unit['id'] = proxy_unit['ip']

            if self.target_url:
                type = re.search('(.*?)://', self.target_url).group(1)
                print 'type is %s' % type
                proxy_unit['type'] = type
                if self.proxy_pool.try_proxy(proxy_unit, self.target_url):
                    self.proxy_pool.insert_data(type, proxy_unit)
                    self.proxy_num += 1
                    if self.proxy_num > self.max_num:
                        return
                    print 'success in proxy: %s' % ('add proxy: %s:%s(%d/%d)' % (proxy_unit['ip'], proxy_unit['port'], self.proxy_num, self.max_num))

            else:
                type = self.simple_try_proxy(proxy_unit)
                print 'type is %s' % type
                if type:
                    proxy_unit['type'] = type
                    self.proxy_pool.insert_data(type, proxy_unit)
                    self.proxy_num += 1
                    if self.proxy_num > self.max_num:
                        return
                    print 'success in proxy: %s' % ('add proxy: %s:%s(%d/%d)' % (proxy_unit['ip'], proxy_unit['port'], self.proxy_num, self.max_num))
        return

    def get_proxy(self):
        proxy_list_page = self.get_proxy_list_page()
        if proxy_list_page is '':
            print 'error in get target page'
        for proxy_item in proxy_list_page:
            target_page = self.url + proxy_item
            print 'begin to scrap target page: %s' % target_page 
            target_page_num = self.get_page_num(target_page)
            if target_page_num is 0:
                print 'error in get target page number'
            print 'target page number is: %d' % target_page_num

            for i in range(1, target_page_num+1):
                str = '/%d.html' % i
                net_url = re.sub(r'/\d+.html', str, target_page)
                print net_url
                self.get_proxy_data(net_url)
                if self.proxy_num > self.max_num:
                    break
                self.proxy_pool.write_data()
            if self.proxy_num > self.max_num:
                break
