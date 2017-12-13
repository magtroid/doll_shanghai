#!/usr/bin/env python
# coding=utf-8
'''Class for proxy pool control

Magtroid @ 2017-07-31 14:03
method for proxy
'''

# import library
import os
import re
import requests
import sys
import time

import datalib
import tools
import common
import mio
import log

# const define
_STATUS_ALIVE = 'alive'
_STATUS_USING = 'using'
_STATUS_DEAD  = 'dead'
_STATUS_RETRY = 'retry'

_PROXY_LIMIT_STRING = ['流量异常',
                       '502 Bad Gateway',
                       'Maximum number of open connections reached',
                       'Failed to get IP address for hostname',]

_TYPE_KEY = 'type'
_SUCC_KEY = 'success'
_FAIL_KEY = 'fail'
_IP_KEY = 'ip'
_PORT_KEY = 'port'
_STATUS_KEY = 'status'
_HISTORY_KEY = 'history'

_CITY_KEY = 'city'
_ANONY_KEY = 'anony'

# main class
class ProxyPool(object):
    # public:
    #   reload_proxy
    #   current_proxy
    #   set_proxy
    #   try_proxy
    #   proxy_num
    #   set_threshold
    #   insert_proxy
    #   delete_proxy
    #   get_page
    #   write_data_lib

    # private:
    #   __init_proxy_history
    #   __switch_proxy
    #   __update_proxy
    #   __reset_proxy
    #   __get_page_from_file
    #   __write_page_to_file

    def __init__(self):
        self.__headers = { 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.37',}
        self.__session = requests.session()
        self.__url_dir = 'urls/'
        self.__proxy = {'http':'',
                        'https':''}
        self.__test_url = {'http': 'http://example.org',
                           'https': 'https://example.org',}
        self.__today = tools.date_list_to_str(tools.get_date())
        self.__request_num = 0
        self.__request_threshold = 150  # set to control proxy
        self.__time_out = 10
        self.__data_lib_file = './datalib/proxy.lib'
        self.__disable_controler = False
        self.__proxy_lib = datalib.DataLib(self.__data_lib_file, self.__disable_controler)
        self.__proxy_lib.load_data_lib()
        self.__proxy_num = self.__proxy_lib.data_num()

    # when update new data lib, use this to merge into current
    def reload_proxy(self):
        self.__update_proxy()
        self.__reset_proxy()

    # print current proxy set
    def current_proxy(self):
        log.VLOG('current proxy is {}'.format(self.__proxy))

    # set proxy set to target proxy
    def set_proxy(self, proxy):
        self.__proxy[proxy[_TYPE_KEY]] = '%s://%s:%s' % (proxy[_TYPE_KEY], \
                                                         proxy[_IP_KEY], \
                                                         proxy[_PORT_KEY])

    # try if target proxy works
    # return page response if success
    def try_proxy(self, proxy, url = None, regex = None):
        url_list = []
        # fill try url list
        if not url:
            if _TYPE_KEY in proxy:
                url_list.append(self.__test_url[proxy[_TYPE_KEY]])
            else:
                for item in self.__test_url.items():
                    url_list.append(item[1])
        else:
            url_list.append(url)
        proxy_tmp = self.__proxy.copy()
        self.__init_proxy_history(proxy)
        # iterate try each type of url
        for surl in url_list:
            proxy[_TYPE_KEY] = tools.get_url_type(surl)
            log.VLOG('try types: {}'.format(proxy[_TYPE_KEY]))
            self.set_proxy(proxy)
            try:
                response = self.__session.get(surl, headers=self.__headers, proxies=self.__proxy, timeout=self.__time_out)
                self.__proxy.update(proxy_tmp)
                proxy[_TYPE_KEY] = tools.get_url_type(surl)
                if regex is not None:
                    if not re.search(regex, response.text):
                        continue
                proxy[_SUCC_KEY] += 1
                proxy[_HISTORY_KEY][self.__today][_SUCC_KEY] += 1
                response = response.text.encode(response.encoding).decode(response.apparent_encoding) if response.text else response.text
                return response
            except requests.exceptions.RequestException:
                pass

        proxy[_FAIL_KEY] += 1
        proxy[_HISTORY_KEY][self.__today][_FAIL_KEY] += 1
        try_number = proxy[_SUCC_KEY] + proxy[_FAIL_KEY]
        per = float(proxy[_SUCC_KEY]) * 100 / try_number if try_number else 0
        log.VLOG('bad proxy: %s:%s, change one (s/f : %d/%d (%.2f))' % (proxy[_IP_KEY], proxy[_PORT_KEY], \
                                                                                proxy[_SUCC_KEY], proxy[_FAIL_KEY], \
                                                                                per))
        self.__proxy.update(proxy_tmp)
        return common.NONE

    # return proxy number of current proxy pool
    def proxy_num(self):
        return self.__proxy_num

    # set shreshold of max tried times of one proxy
    def set_threshold(self, num):
        self.__request_threshold = num

    # insert proxy
    def insert_proxy(self, lkey, proxy_data):
        if self.__proxy_lib.insert_data(lkey, proxy_data, _IP_KEY):
            self.__proxy_num += 1

    # delete proxy
    def delete_proxy(self, lkey):
        if self.__proxy_lib.delete_data(lkey):
            self.__proxy_num -= 1

    # return page using all proxy necessary
    def get_page(self, url, get_page_type = None, regex = None):
        response = common.NONE
        if get_page_type:
            response = self.__get_page_from_file(url, get_page_type)
            if response:
                return response

        exit = False
        while not exit:
            if self.__request_num < self.__request_threshold:
                try:
                    response = self.__session.get(url, headers=self.__headers, proxies=self.__proxy, timeout=self.__time_out)
                    response = response.text.encode(response.encoding).decode(response.apparent_encoding) if response.text else response.text
                except requests.exceptions.RequestException:
                    log.VLOG('bad proxy, switch proxy')
                    response = self.__switch_proxy(url)
                    self.__request_num = 0
            else:
                log.VLOG('request control, switch proxy')
                response = self.__switch_proxy(url)
                self.__request_num = 0
            self.__request_num += 1

            if response is common.NONE:
                log.VLOG('get page failed, try to reload proxy')
                time.sleep(1)
                # self.__request_num = self.__request_threshold  # TODO
                self.reload_proxy()
                exit = False
            elif response == '':  # TODO(magtroid): add logic for restriction
                exit = True
            else:
                limit_flag = False
                for limit_str in _PROXY_LIMIT_STRING:
                    if response.find(limit_str) != common.FIND_NONE:
                        limit_flag = True
                        self.__request_num = self.__request_threshold
                if regex is not None:
                    if not re.search(regex, response):
                        limit_flag = True
                        self.__request_num = self.__request_threshold
                if limit_flag is False:
                    exit = True

        # write pages
        if get_page_type and response is not common.NONE:
            self.__write_page_to_file(url, response)
        return response

    # write data lib
    def write_data_lib(self):
        self.__proxy_lib.write_data_lib()

    # initial proxy history
    def __init_proxy_history(self, proxy):
        if _HISTORY_KEY not in proxy:
            proxy[_HISTORY_KEY] = dict()
        if self.__today not in proxy[_HISTORY_KEY]:
            proxy[_HISTORY_KEY][self.__today] = dict()
            proxy[_HISTORY_KEY][self.__today][_SUCC_KEY] = 0
            proxy[_HISTORY_KEY][self.__today][_FAIL_KEY] = 0

    # switch to next available proxy
    # and return the page
    def __switch_proxy(self, url):
        url_type = tools.get_url_type(url)
        url_type_path = datalib.form_lkey([datalib.DATA_KEY, url_type])
        response = common.NONE

        if self.__proxy_lib.lhas_key(url_type_path):
            proxy_lib = self.__proxy_lib.get_data(url_type_path)
            loop = 0
            # loop 2 times, 1st: dead -> retry 2nd: retry -> dead
            # to try all proxy circulation
            while response is common.NONE:
                loop += 1
                for ip in proxy_lib.keys():
                    # not selected: alive -> using/dead
                    #               using -> dead
                    #               dead  -> retry (loop1)
                    #               retry -> using/dead (loop2)
                    if response is common.NONE:
                        if proxy_lib[ip][_STATUS_KEY] == _STATUS_ALIVE:
                            response = self.try_proxy(proxy_lib[ip], url)
                            if response is not common.NONE:
                                self.set_proxy(proxy_lib[ip])
                                proxy_lib[ip][_STATUS_KEY] = _STATUS_USING
                            else:
                                proxy_lib[ip][_STATUS_KEY] = _STATUS_DEAD
                        elif proxy_lib[ip][_STATUS_KEY] == _STATUS_USING:
                            proxy_lib[ip][_STATUS_KEY] = _STATUS_DEAD
                        elif proxy_lib[ip][_STATUS_KEY] == _STATUS_DEAD:
                            if loop is 1:
                                proxy_lib[ip][_STATUS_KEY] = _STATUS_RETRY  # set retry for second loop
                            elif loop is 2:
                                continue
                        else:  # retry
                            if loop is 1:  # wait for second loop
                                continue
                            elif loop is 2:
                                response = self.try_proxy(proxy_lib[ip], url)
                                if response is not common.NONE:
                                    self.set_proxy(proxy_lib[ip])
                                    proxy_lib[ip][_STATUS_KEY] = _STATUS_USING
                                else:
                                    proxy_lib[ip][_STATUS_KEY] = _STATUS_DEAD
                    # selected : alive
                    #            using -> dead
                    #            dead  -> retry
                    #            retry -> alive (loop2)
                    else:
                        if proxy_lib[ip][_STATUS_KEY] == _STATUS_ALIVE:
                            continue
                        elif proxy_lib[ip][_STATUS_KEY] == _STATUS_USING:
                            proxy_lib[ip][_STATUS_KEY] = _STATUS_DEAD
                        elif proxy_lib[ip][_STATUS_KEY] == _STATUS_DEAD:
                            proxy_lib[ip][_STATUS_KEY] = _STATUS_RETRY  # set retry for second loop
                        else:  # retry
                            if loop is 1:
                                continue
                            elif loop is 2:
                                proxy_lib[ip][_STATUS_KEY] = _STATUS_ALIVE  # set retry for second loop
                if loop is 2:
                    break
            if response is common.NONE:
                log.VLOG('no proxy available')
                self.__reset_proxy()
                return response
            else:
                log.VLOG('switch proxy success, switch to %s' % self.__proxy[url_type])
                return response
        else:
            log.VLOG('bad url type: %s: %s' % (url_type, url))
            self.__reset_proxy()
            return response

    # update proxy data lib with new dict
    # and update data number
    def __update_proxy(self, file = None):
        if not file:
            file = self.__data_lib_file
        self.__proxy_lib.update_data_lib(file)
        self.__proxy_num = self.__proxy_lib.data_num()

    # reset proxy to empty
    # reset all proxy data status to alive
    def __reset_proxy(self):
        log.VLOG('reset proxy')
        for url_type in self.__proxy.keys():
            self.__proxy[url_type] = ''
        data = self.__proxy_lib.get_data()
        for url_type in data.keys():
            for ip in data[url_type].keys():
                data[url_type][ip][_STATUS_KEY] = _STATUS_ALIVE

    # read page from exists file
    def __get_page_from_file(self, url, type):
        response = ''
        name = re.sub('^.*?://', '',  url)
        name = re.sub('/', '-', name)
        name = self.__url_dir + name
        if os.path.isfile(name):
            if type == common.URL_READ:
                with open(name) as fp_in:
                    lines = fp_in.readlines()
                    for line in lines:
                        response = response + line
            elif type == common.URL_READ_THROUGH:
                response = common.URL_EXISTS
            else:  # common.URL_WRITE
                pass
        return response

    # write page to file
    def __write_page_to_file(self, url, response):
        name = re.sub('^.*?://', '',  url)
        name = re.sub('/', '-', name)
        name = self.__url_dir + name
        with open(name, 'w') as fp_out:
            fp_out.writelines(response)

# data process class
class ProxyPoolData(object):
    # public:
    #   display_data
    # private:
    #   __overview_data
    #   __display_detail_data
    def __init__(self):
        self.__data_lib_file = './datalib/proxy.lib'
        self.__disable_controler = True
        self.__proxy_lib = datalib.DataLib(self.__data_lib_file, self.__disable_controler)
        self.__proxy_lib.load_data_lib()

    # display proxy data lib
    def display_data(self):
        self.__overview_data()
        self.__display_detail_data()

    # display overview data in proxy data lib
    def __overview_data(self):
        data = self.__proxy_lib.get_data()
        for type_items in data.items():
            log.VLOG('proxy type: %s' % type_items[0])
            for proxy_item in sorted(type_items[1].items(), key = lambda d:d[1][_SUCC_KEY], reverse = True):
                proxy = proxy_item[1]
                try_number = proxy[_SUCC_KEY] + proxy[_FAIL_KEY]
                per = float(proxy[_SUCC_KEY]) * 100 / try_number if try_number else 0
                log.VLOG('\t%-15s:%-5s (s/f : %3d/%-3d (%.2f))' % (proxy[_IP_KEY], proxy[_PORT_KEY],
                                                                   proxy[_SUCC_KEY], proxy[_FAIL_KEY],
                                                                   per))

    # choose one proxy and display detail
    def __display_detail_data(self):
        while True:
            command = mio.choose_command()
            if command == 'cancel' or command == 'q':
                log.VLOG('canceled...')
                break
            data = self.__proxy_lib.get_data()
            for type_items in data.items():
                if command in type_items[1]:
                    proxy = type_items[1][command]
                    try_number = proxy[_SUCC_KEY] + proxy[_FAIL_KEY]
                    per = float(proxy[_SUCC_KEY]) * 100 / try_number if try_number else 0
                    log.VLOG('\t%-15s:%-5s (s/f : %3d/%-3d (%.2f))' % (proxy[_IP_KEY], proxy[_PORT_KEY],
                                                                       proxy[_SUCC_KEY], proxy[_FAIL_KEY],
                                                                       per))
                    log.VLOG('\ttypes:%-6s  city:%-12s  anony:%-10s' % (proxy[_TYPE_KEY],
                                                                        proxy[_CITY_KEY],
                                                                        proxy[_ANONY_KEY]))
                    if _HISTORY_KEY in proxy:
                        history = proxy[_HISTORY_KEY]
                        for history_item in history.items():
                            log.VLOG('\t\t{0:>12s} s:f {1:3d}/{2:<3d}'.format(history_item[0],
                                                                              history_item[1][_SUCC_KEY],
                                                                              history_item[1][_FAIL_KEY]))
                    else:
                        log.VLOG('new proxy, no history yet')
