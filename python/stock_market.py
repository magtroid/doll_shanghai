#!/usr/bin/env python
# coding=utf-8
'''Module for stock market data scrap

Magtroid @ 2017-07-27 01:30
method for stock market'''

# import library
from bs4 import BeautifulSoup
import common
import datalib
import proxypool
import stock
import tools
import log

# process switch
_PROCESS_STOCK_LIST = True  # get or update new stock list
_UPDATE_STOCK_ITEM = True

# const define
# stock domain
_ZS_CLASS = 'zs'
_SH_CLASS = 'ha'
_SZ_CLASS = 'sa'
_CY_CLASS = 'gem'

_ID_KEY   = datalib.DATA_FEATURE
_NAME_KEY = 'name'
_HREF_KEY = 'href'
_TAPE_KEY = 'tape'

# tape id
_SH_TAPE_ID = '000001'
_SZ_TAPE_ID = '399001'
_CY_TAPE_ID = '399006'

# main class
class StockMarket(object):
    # public:
    #   get_stock_market_data  # main function
    # private:
    #   __get_stock_list
    #   __parse_class_stock_list
    #   __insert_stock_data
    #   __scrap_tape_data
    #   __scrap_stock_market_data
    #   __write_data_lib

    def __init__(self, vlog = 0, proxy_pool = None):
        self.__vlog = log.VLOG(vlog)
        self.__stock_market_url = 'http://app.finance.ifeng.com/hq/list.php'
        if proxy_pool == None:
            self.__proxy_pool = proxypool.ProxyPool()
        else:
            self.__proxy_pool = proxy_pool
        self.__data_lib_file = './datalib/stock_list.lib'
        self.__disable_controler = True  # TODO
        self.__stock_market_lib = datalib.DataLib(self.__data_lib_file, self.__disable_controler)
        self.__stock_market_lib.load_data_lib()
        self.__get_page_type = common.URL_READ
        self.__stock_market_class = [_ZS_CLASS, _SH_CLASS , _SZ_CLASS, _CY_CLASS]
        self.__tape_set = {_SH_TAPE_ID, _SZ_TAPE_ID, _CY_TAPE_ID}
        self.__get_stock_list(_PROCESS_STOCK_LIST)

    # scrap stock data
    def get_stock_market_data(self):
        self.__scrap_stock_market_data()
        self.__write_data_lib()
        print 'done stock market'

    # get stock list from the page
    # switch to control this function work
    def __get_stock_list(self, switch = None):
        if not switch:
            return
        for sclass in self.__stock_market_class:
            if sclass == _ZS_CLASS:
                self.__parse_class_stock_list(sclass, self.__tape_set)
            else:
                self.__parse_class_stock_list(sclass)
        print 'all stock number %d' % self.__stock_market_lib.data_num()

    # parse stocks from urls
    # index is a set to choose which stock to get, empty for all
    def __parse_class_stock_list(self, sclass, index = None):
        class_url = '%s?type=stock_a&class=%s' % (self.__stock_market_url, sclass)
        page = self.__proxy_pool.get_page(class_url, self.__get_page_type)
        if not page:
            print 'failed to scrap class page'
            return

        soup = BeautifulSoup(page, common.HTML_PARSER)
        for stock_element in soup.select('div.result ul li'):
            stock_unit = dict()
            stock_text = tools.ultra_encode(stock_element.get_text())
            stock_id = stock_text.split('(')[1][:-1] 
            stock_name = stock_text.split('(')[0]
            stock_href = tools.parse_href_url(str(stock_element.a[common.HREF_KEY]), class_url)
            stock_unit[_ID_KEY] = stock_id
            stock_unit[_NAME_KEY] = stock_name
            stock_unit[_HREF_KEY] = stock_href
            if not index or stock_id in index:
                self.__insert_stock_data(sclass, stock_unit)

    # insert stock data
    def __insert_stock_data(self, lkey, stock_data):
        self.__stock_market_lib.insert_data(lkey, stock_data, _ID_KEY)

    # get tape data
    def __scrap_tape_data(self):
        data = self.__stock_market_lib.get_data()
        for tape_item in data[_ZS_CLASS].items():
            stock_code = tape_item[1][_HREF_KEY].split('/')[-2]  # stock/sh000001/index.shtml
            print 'scrap tape: {stock_code} ({stock_name})'.format(stock_code = stock_code, \
                                                                   stock_name = tape_item[1][_NAME_KEY])
            # get link new lib
            if not tape_item[1].has_key(datalib.LINK_FEATURE):
                stock_data = stock.Stock(stock_code, proxy_pool = self.__proxy_pool)
                if stock_data.get_stock_data():
                    tape_item[1][datalib.LINK_FEATURE] = stock_data.get_stock_lib()

    # get stock data
    def __scrap_stock_market_data(self):
        data = self.__stock_market_lib.get_data()
        for stock_class in self.__stock_market_class:
            stock_num = 0
            class_data = data[stock_class]
            for stock_item in class_data.items():
                stock_num += 1
                stock_code = stock_item[1][_HREF_KEY].split('/')[-2]  # stock/sh000001/index.shtml
                print 'scrap stock: {stock_code} ({stock_name}) ({num}/{all_num})'.format( \
                                                                                   stock_code = stock_code, \
                                                                                   stock_name = stock_item[1][_NAME_KEY], \
                                                                                   num = stock_num, \
                                                                                   all_num = len(class_data))
                # get link new lib
                if not stock_item[1].has_key(datalib.LINK_FEATURE) or \
                   stock_item[1][datalib.LINK_FEATURE] == None:
                    stock_data = stock.Stock(stock_code, proxy_pool = self.__proxy_pool)
                else:
                    lstock_code = stock_item[1][datalib.LINK_FEATURE].split('/')[-1].split('.')[0]
                    stock_data = stock.Stock(lstock_code, proxy_pool = self.__proxy_pool)
                if stock_data.get_stock_data():
                    stock_data.write_stock_data()
                    stock_item[1][datalib.LINK_FEATURE] = stock_data.lib_file()

    # write data lib
    def __write_data_lib(self, config = None):
        self.__stock_market_lib.write_data_lib()
        self.__proxy_pool.write_data_lib()
