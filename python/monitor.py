#!/usr/bin/env python
# coding=utf-8
'''Module for stock process data

Magtroid @ 2017-09-05 10:25
monitor stock and process
'''

# import library
import controler
import common
import datalib
import log
import proxypool
import re
import tools

# const define
_URL_KEY = 'url'

_STATUS_ALIVE = 'alive'
_STATUS_DEAD = 'dead'

_LAST_TIME = 'last_time'
_LAST_TRANS = 'last_trans'

# main class
class StockMonitor(object):
    # public
    #   stock_monitor  # main function
    # private
    #   __commond_control
    #   __new_stock
    #   __display_price
    
    def __init__(self, vlog = 0, proxy_pool = None):
        self.__vlog = log.VLOG(vlog)
        if proxy_pool == None:
            self.__proxy_pool = proxypool.ProxyPool()
        else:
            self.__proxy_pool = proxy_pool
        self.__data_lib_file = './datalib/property.lib'
        self.__disable_controler = True  # TODO
        self.__property_lib = datalib.DataLib(self.__data_lib_file, self.__disable_controler)
        self.__property_lib.load_data_lib()
        self.__get_page_type = common.URL_READ
        self.__url = 'http://api.finance.ifeng.com/amin/?code='
        self.__type = '&type=now'
        self.__max_stock_monitor = 4

        self.__stock_list = dict()  # TODO load stock list from datalib
        self.__status = _STATUS_ALIVE

    # monitor stock and property
    def stock_monitor(self):
        quit = False
        while not quit:
            self.__commond_control()
            self.__display_price()

    # receive commond and control
    def __commond_control(self):
        commond = tools.kbhit()
        if commond:
            if commond in self.__stock_list:
                del self.__stock_list[commond]
            elif len(self.__stock_list) >= self.__max_stock_monitor:
                self.__vlog.VLOG("full stocks")
            else:
                stock = self.__new_stock(commond)
                if self.__proxy_pool.get_page(stock[_URL_KEY], self.__get_page_type):
                    self.__stock_list[commond] = stock

    # create a new stock to monitor
    def __new_stock(self, stock_id):
        stock = dict()
        stock[_URL_KEY] = self.__url + stock_id + self.__type
        stock[_LAST_TIME] = ''
        stock[_LAST_TRANS] = ''
        return stock

    # display each stock price
    def __display_price(self):
        stocks_price = tools.get_time_str(tools.TIME_HOUR, tools.TIME_SECOND, ':')
        for stock_item in self.__stock_list.items():
            response = self.__proxy_pool.get_page(stock_item[1][_URL_KEY], self.__get_page_type)
            price = re.sub('"', '', response[1:-1].encode('utf-8')).split(',')
            ctime = re.sub(':\d\d$', '', price[0].split()[1])
            if not stock_item[1][_LAST_TIME] or stock_item[1][_LAST_TIME] != ctime:
                transaction = int(price[6])
            else:
                transaction = int(price[6]) - stock_item[1][_LAST_TRANS]
            stocks_price += '  |  {stock_id} {price:7s} {rate:7s} {trans:7d}'.format(stock_id = stock_item[0], \
                                                                                     price = price[2], \
                                                                                     rate = price[3], \
                                                                                     trans = transaction)
            stock_item[1][_LAST_TIME] = ctime
            stock_item[1][_LAST_TRANS] = int(price[6])
        self.__vlog.VLOG(stocks_price)
        tools.sleep(3.2)
