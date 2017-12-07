#!/usr/bin/env python
# coding=utf-8

import proxypool
import re
import requests
import sys
import tools
sys.path.append('./gflags')
import gflags

FLAGS = gflags.FLAGS
gflags.DEFINE_string('proxy_type', 'https', 'http / https')

class Proxy(object):
    def __init__(self):
        self.url = 'http://www.xicidaili.com'
        self.max_num = 200
        self.target_type = FLAGS.proxy_type
        self.proxy_pool = proxypool.ProxyPool()

    def get_target_page(self):
        target_page = ''
        success = False
        page = self.proxy_pool.get_page(self.url)
        while not success:
            if self.target_type == 'http':
                net_search = re.search('<h2>HTTP代理IP.*?more" href="(.*?)"', page, re.S)
            elif self.target_type == 'https':
                net_search = re.search('<h2>HTTPS代理IP.*?more" href="(.*?)"', page, re.S)
            else:
                print('error proxy type')
                return target_page

            if net_search:
                success = True
                net = net_search.group(1)
                target_page = self.url + net
            else:
                page = self.proxy_pool.switch_proxy(self.url)
                if not page:
                    print('error to scrap proxy targe page')
                    return target_page
        return target_page

    def get_page_num(self, url):
        page_num = 0
        page = self.proxy_pool.get_page(url)
        net_search = re.search('class="pagination.*href=".*?(\d+)">\d+', page, re.S)
        if net_search:
            page_num = int(net_search.group(1))
        else:
            print('error to scrap page number')
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
        proxy_search = re.search('(<table id="ip_list".*?</table>)', page, re.S)
        while not proxy_search:
            page = self.proxy_pool.switch_proxy(url)
            if not page:
                print('no proxy for url')
                return False
            proxy_search = re.search('(<table id="ip_list".*?</table>)', page, re.S)
        proxy_search = proxy_search.group(1)
        proxy_list = re.findall('(<tr class.*?</tr>)', proxy_search, re.S)
        count = 0
        for sproxy in proxy_list:
            count += 1
            proxy_unit = dict()
            pattern_list = re.findall('<td.*?>(.*?)</td>', sproxy, re.S)
            country_search = re.search('alt.*?"(.*?)"', pattern_list[0], re.S)
            if country_search:
                proxy_unit['country'] = country_search.group(1)
            else:
                proxy_unit['country'] = ''
            proxy_unit['ip'] = pattern_list[1]
            proxy_unit['port'] = pattern_list[2]
            print('schedule %d/%d (%s:%s)' % (count, len(proxy_list), proxy_unit['ip'], proxy_unit['port']))
            province_search = re.search('href.*?>(.*?)<', pattern_list[3], re.S)
            if province_search:
                proxy_unit['province'] = province_search.group(1)
            else:
                proxy_unit['province'] = ''
            proxy_unit['anony'] = pattern_list[4]
            if not proxy_unit['anony'] == '高匿':
                print('not anony, change one')
                continue
            proxy_unit['type'] = pattern_list[5].lower()
            speed_search = re.search('title="(.*?)"', pattern_list[6], re.S)
            if speed_search:
                proxy_unit['speed'] = speed_search.group(1)
            else:
                proxy_unit['speed'] = ''
            connect_search = re.search('title="(.*?)"', pattern_list[7], re.S)
            if connect_search:
                proxy_unit['connect'] = connect_search.group(1)
            else:
                proxy_unit['connect'] = ''
            proxy_unit['alive'] = pattern_list[8]
            proxy_unit['success'] = 0
            proxy_unit['fail'] = 0
            proxy_unit['status'] = 'alive'

            if self.proxy_pool.simple_try_proxy(proxy_unit):
                if self.proxy_pool.insert_data(proxy_unit) > self.max_num:
                    return True
                print('success in proxy: %s' % ('add proxy: %s:%s(%d/%d)' % (proxy_unit['ip'], proxy_unit['port'], self.proxy_pool.proxy_num, self.max_num)))
        return False

    def get_proxy(self):
        target_page = self.get_target_page()
        if target_page is '':
            print('error in get target page')
        print('begin to scrap target page: %s' % target_page)
        target_page_num = self.get_page_num(target_page)
        if target_page_num is 0:
            print('error in get target page number')
        print('target page number is: %d' % target_page_num)

        for i in range(1, target_page_num+1):
            net_url = '%s/%d' % (target_page, i)
            print(net_url)
            if self.get_proxy_data(net_url):
                break
            self.proxy_pool.write_data()
