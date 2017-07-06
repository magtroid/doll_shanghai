#!/usr/bin/env python
# coding=utf-8
'''Module for lianjia data scrap

Magtroid @ 2017-06-21 20:23
methods for lianjia'''

import common
import datalib
import proxypool
import re
import requests
import sys
import tools

class LianJia(object):
    def __init__(self):
        self.city = 'bj'
        self.http = 'https://'
        self.lianjia = '.lianjia.com'
        self.city_url = self.http + self.city + self.lianjia
        self.start_date = []
        self.end_date = []
        self.region = dict()
        self.region_number = 0
        self.proxy_pool = proxypool.ProxyPool()
        self.data = datalib.DataLib('./datalib/lianjia.lib')
        self.data.load_data()
        self.log = 0

    def get_duration(self):
        flag = 'y'
        while flag is 'y':
            print 'insert time duration (1 day/1 week/xxxx.xx.xx~yyyy.yy.yy/update)'
            print '\tor insert "n/N" to cancel'
            time = sys.stdin.readline().strip()
            date = tools.get_date()
            if time == '1 day':
                self.start_date = tools.get_date(-1)
                self.end_date = tools.get_date()
            elif time == '1 week':
                self.start_date = tools.get_date(-7)
                self.end_date = tools.get_date()
            elif re.match('^\d{4}\.\d{2}\.\d{2}~\d{4}\.\d{2}\.\d{2}$', time):
                start_date = map(int, time.split('~')[0].split('.'))
                end_date = map(int, time.split('~')[1].split('.'))
                if tools.date_valid(start_date) and \
                   tools.date_valid(end_date) and \
                   tools.date_compare(start_date, end_date) <= 0:
                    self.start_date = start_date
                    self.end_date = end_date
                else:
                    print 'insert date invalid'
                    continue
            elif time == 'update':
                if not self.data.lhas_key('end_date'):
                    self.start_date = tools.get_date(-2000)
                else:
                    self.start_date = self.data['end_date']
                self.end_date = tools.get_date()
            elif time is 'n' or time is 'N':
                self.start_date = []
                self.end_date = []
            else:
                print 'not support this type'
                continue
            flag = 'n'
        if len(self.start_date) is 0 or (self.end_date) is 0:
            return False
        else:
            print 'start to get data in time duration: %s to %s' % (' '.join(str(i) for i in self.start_date), ' '.join(str(j) for j in self.end_date))
            return True

    def get_subregion(self, url):
        city_url = re.sub('(^.*?)/chengjiao.*', r'\1', url)
        page = self.proxy_pool.get_page(url, tools.test_for_write)
        subregion_line = re.search('.*?<div data-role="ershoufang".*?<div>.*?<div>(.*?)</div', page, re.S).group(1)
        subregion_list = re.findall('href="(.*?)" >(.*?)<', subregion_line)
        subregion = dict()
        subregion_count = 0
        for ssubregion in subregion_list:
            subregion_count += 1
            self.region_number += 1
            print '\tsub region %d/%d %s' % (subregion_count, len(subregion_list), ssubregion[1])
            if re.search('^/chengjiao', ssubregion[0]):
                subregion_url = city_url + ssubregion[0]
            else:
                subregion_url = ssubregion[0]
            subregion[subregion_url] = ssubregion[1]
        return subregion

    def get_region(self):
        print 'begin to get region'
        cjurl = self.city_url + '/chengjiao'
        page = self.proxy_pool.get_page(cjurl, tools.test_for_write)
        region_line = re.search('.*?<div data-role="ershoufang"(.*?)</div>', page, re.S).group(1)
        region_list = re.findall('href="(.*?)".*title="(.*?)"', region_line)
        region_count = 0
        for sregion in region_list:
            region_count += 1
            name = re.sub(r'成交二手房', '', sregion[1])
            print 'region %d/%d %s' % (region_count, len(region_list), name)
            if re.search('^/chengjiao', sregion[0]):
                region_url = self.city_url + sregion[0]
            else:
                region_url = sregion[0]
            self.region[region_url] = dict()
            self.region[region_url]['name'] = name
            self.region[region_url]['subregion'] = self.get_subregion(region_url)

        if self.log is 1:
            for region in self.region.keys():
                print region
                for each in self.region[region]['subregion'].items():
                    print '\t%s\t%s' % (each[0], each[1])

        print 'all %d regions' % self.region_number

    def get_page_num(self, url):
        page_num = 0
        page = self.proxy_pool.get_page(url)
        page_num_search = re.search('^.*totalPage":(\d+).*$', page, re.S)
        if page_num_search:
            page_num = page_num_search.group(1)
        return int(page_num)

    def in_search_range(self, date):
        if tools.date_compare(self.start_date, date) <= 0 and \
           tools.date_compare(date, self.end_date) <= 0:
            return True
        else:
            return False

    def parse_data(self, text, region):
        data_line_search = re.search('<div class="content"(.*)<div class="footer', text, re.S)
        if data_line_search:
            data_line = data_line_search.group(1)
        else:
            print 'error data line'
            return
        chengjiao_data = re.findall(r'<li>(.*?)</li>', data_line)
        for i in range(len(chengjiao_data)):
            deal_unit = dict()
            id_search = re.search(r'title.*?chengjiao/(\d+)', chengjiao_data[i], re.S)
            if id_search:
                id = id_search.group(1)
            else:
                print 'error id'
                continue
            # if exists data
            if self.data.lhas_key('data__%s' % id):
                print 'id exist'
                continue
            deal_unit['id'] = id
            deal_unit['region'] = region['region']
            deal_unit['subregion'] = region['subregion']

            # regex data
            match_date = re.search(r'dealDate">(.*?)<', chengjiao_data[i], re.S)
            match_deal = re.search(r'totalPrice"><span class=\'number\'>(.*?)<', chengjiao_data[i], re.S)
            match_unit = re.search(r'unitPrice.*?number">([\d.]+)', chengjiao_data[i], re.S)
            match_hang = re.search(r'dealCycleTxt"><span>.*?([\d.]+)', chengjiao_data[i])

            # if date in search range
            if match_date and not self.in_search_range(map(int, match_date.group(1).split('.'))):
                print 'not in search range'
                continue

            if match_date:
                deal_unit['date'] = map(int, match_date.group(1).split('.'))
            else:
                deal_unit['date'] = []

            if match_deal:
                deal_unit['deal'] = float(match_deal.group(1))
            else:
                deal_unit['deal'] = 0
            if match_unit:
                deal_unit['unit'] = float(match_unit.group(1))
            else:
                deal_unit['unit'] = 0
            if match_hang:
                deal_unit['hang'] = float(match_hang.group(1))
            else:
                deal_unit['hang'] = 0
            print deal_unit
            self.data.insert_data('data', deal_unit)

    def get_data(self, url, region):
        page = self.proxy_pool.get_page(url, tools.test_for_write)
        while re.search('流量异常', page, re.S):
            page = self.proxy_pool.switch_proxy(url, tools.test_for_write)
        self.parse_data(page, region)

    def aplay_data(self, data):
        for i in range(len(data)):
            print str(data[i][0]) + '\t' + \
                  str(data[i][1]) + '\t' + \
                  str(data[i][2])

    def get_chengjiao(self):
        if not self.get_duration():
            return
        
        self.get_region()

        region = dict()
        for sregion in self.region.items():
            region['region'] = sregion[1]['name']
            for ssubregion in sregion[1]['subregion'].items():
                region['subregion'] = ssubregion[1]
                print 'scrap region: %s' % ssubregion[0]

                page = self.get_page_num(ssubregion[0])
                for i in range(1, int(page)):
                    print '\tscrap page: %d/%d' % (i, page)
                    dataurl = '%s/pg%d' % (sregion[0], i)
                    dataurl = re.sub('(?<!:)/+', '/', dataurl)
                    self.get_data(dataurl, region)
                    self.data.write_data_lib()
                    print 'all data number: %d' % self.data.data_num
