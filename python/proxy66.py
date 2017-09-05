#!/usr/bin/env python
# coding=utf-8
'''
Class for proxy scrap in 66ip net

Magtroid @ 2017-08-01 10:23
method for proxy
'''

#import library
from bs4 import BeautifulSoup
import common
import proxypool
import re
import requests
import sys
import tools

# const define
# proxy keys
_IP_KEY = 'ip'
_PORT_KEY = 'port'
_TYPE_KEY = 'type'
_STATUS_KEY = 'status'
_CITY_KEY = 'city'
_ANONY_KEY = 'anony'
_SUCC_KEY = 'success'
_FAIL_KEY = 'fail'
_SPEED_KEY = 'speed'

_STATUS_DEFAULT = 'alive'

# main class
class Proxy(object):
    # public:
    #   simple_try_proxy
    #   get_proxy
    # private:
    #   __get_proxy_domain_list
    #   __get_page_num
    #   __get_proxy_data
    def __init__(self, proxy_pool = None):
        self.__url = 'http://www.66ip.cn'
        # self.__target_url = 'https://bj.lianjia.com/chengjiao'
        self.__target_url = 'http://api.finance.ifeng.com/akmonthly/?code=sh603737&type=last'
        self.__regex = '^{"record.*}$'
        # self.__target_url = 'http://www.66ip.cn'
        self.__max_proxy_num = 20
        self.__proxy_num = 0
        self.__max_search_page = 5
        self.__proxy_try_time = 5
        if proxy_pool == None:
            self.__proxy_pool = proxypool.ProxyPool()
        else:
            self.__proxy_pool = proxy_pool

    def simple_try_proxy(self, proxy):
        type = ''
        proxy['type'] = 'http'
        if self.__proxy_pool.simple_try_proxy(proxy):
            type = 'http'
        if not type:
            type = 'https'
            if self.__proxy_pool.simple_try_proxy(proxy):
                type = 'https'
        return type

    # get page and parse proxy from net
    def get_proxy(self):
        proxy_domain_list = self.__get_proxy_domain_list()
        if proxy_domain_list:
            print 'error in get target page'

        domain_id = 0
        for proxy_domain in proxy_domain_list:
            domain_id += 1
            domain_url = tools.parse_href_url(proxy_domain, self.__url)
            print 'begin to scrap target page: %s' % domain_url
            domain_page_num = self.__get_page_num(domain_url)
            max_search_page = self.__max_search_page if domain_page_num > self.__max_search_page else domain_page_num
            print 'domain page number is: %d, scrap first %d pages' % (domain_page_num, max_search_page)

            for page_num in range(max_search_page):
                # loop proxy try times to scrap proxy
                for loop in range(self.__proxy_try_time):
                    page_url = '%s/%d.html' % (domain_url, page_num + 1)
                    print 'begin to scrap page: %s (loop %d/%d)' % (page_url, loop + 1, self.__proxy_try_time)
                    page = self.__proxy_pool.get_page(page_url)
                    if not page:
                        print 'failed to get page'
                    else:
                        self.__get_proxy_data(page)

                    if self.__proxy_num > self.__max_proxy_num:
                        print 'enough proxy, finish!'
                        self.__proxy_pool.write_data_lib()
                        break
                if self.__proxy_num > self.__max_proxy_num:
                    break
            if self.__proxy_num > self.__max_proxy_num:
                break

    # get proxy domain of proxy 66ip net
    def __get_proxy_domain_list(self):
        proxy_domain_list = []
        page = self.__proxy_pool.get_page(self.__url, common.URL_READ)
        if not page:
            print 'error to scrap proxy targe page'
        else:
            soup = BeautifulSoup(page, common.HTML_PARSER)
            for element in soup.select('td ul li a'):
                proxy_domain_list.append(re.sub('/\d+\.html', '', element[common.HREF_KEY]))
        return proxy_domain_list

    # get page number of target page
    def __get_page_num(self, url):
        page_num = 0
        page = self.__proxy_pool.get_page(url, common.URL_READ)
        if not page:
            print 'get page number failed %s: ' % url
        else:
            soup = BeautifulSoup(page, common.HTML_PARSER)
            # last second is the last page
            page_num = int(soup.select('div[id="PageList"] a')[-2].get_text())
        return page_num

    # parse proxy from target page
    def __get_proxy_data(self, page):
        soup = BeautifulSoup(page, common.HTML_PARSER)
        proxy_list = soup.select('table[bordercolor="#6699ff"] tr')  # table is the direct children of [document]
        # 1st is the catalog 
        for proxy in proxy_list[1:]:
            proxy_tds = [str(proxy_td.get_text()) for proxy_td in proxy.select('td')]

            proxy_unit = dict()
            proxy_unit[_IP_KEY] = proxy_tds[0]
            proxy_unit[_PORT_KEY] = proxy_tds[1]
            proxy_unit[_SUCC_KEY] = 0
            proxy_unit[_FAIL_KEY] = 0

            if self.__proxy_pool.try_proxy(proxy_unit, self.__target_url, regex = self.__regex):
                proxy_unit[_CITY_KEY] = proxy_tds[2]
                proxy_unit[_ANONY_KEY] = proxy_tds[3]
                proxy_unit[_STATUS_KEY] = _STATUS_DEFAULT
                proxy_unit[_SPEED_KEY] = 0
                proxy_unit[_SUCC_KEY] = 0  # reset success count
                self.__proxy_pool.insert_proxy(proxy_unit[_TYPE_KEY], proxy_unit)
                self.__proxy_num += 1
                print 'success insert proxy: %s' % ('add proxy: %s:%s(%d/%d)' % (proxy_unit[_IP_KEY], proxy_unit[_PORT_KEY], self.__proxy_num, self.__max_proxy_num))
                if self.__proxy_num > self.__max_proxy_num:
                    break
