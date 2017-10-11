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
    #   get_stock_map_list
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
        self.__proxy_pool.set_threshold(15000)
        self.__data_lib_file = './datalib/stock_list.lib'
        self.__disable_controler = True  # TODO
        self.__stock_market_lib = datalib.DataLib(self.__data_lib_file, self.__disable_controler)
        self.__stock_market_lib.load_data_lib()
        self.__get_page_type = common.URL_READ
        self.__stock_market_class = [_CY_CLASS]  # _ZS_CLASS, _SH_CLASS , _SZ_CLASS, _CY_CLASS]
        self.__tape_set = {_SH_TAPE_ID, _SZ_TAPE_ID, _CY_TAPE_ID}
        self.__get_stock_list(_PROCESS_STOCK_LIST)

    # scrap stock data
    def get_stock_market_data(self):
        self.__scrap_stock_market_data()
        self.__write_data_lib()
        self.__vlog.VLOG('done stock market')

    def get_stock_map_list(self):
        map_list = dict()
        data = self.__stock_market_lib.get_data()
        stock_map_list_tape = [_SH_CLASS, _SZ_CLASS, _CY_CLASS]
        for tape in stock_map_list_tape:
            tape_stocks = data[tape]
            for stock_item in tape_stocks.items():
                stock_name = stock_item[1][_NAME_KEY]
                if len(stock_name) != 0 and stock_name not in map_list:
                    map_list[stock_name] = stock.parse_stock_code(stock_item[0])
        return map_list

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
        self.__vlog.VLOG('all stock number %d' % self.__stock_market_lib.data_num())

    # parse stocks from urls
    # index is a set to choose which stock to get, empty for all
    def __parse_class_stock_list(self, sclass, index = None):
        class_url = '%s?type=stock_a&class=%s' % (self.__stock_market_url, sclass)
        page = self.__proxy_pool.get_page(class_url, self.__get_page_type)
        if not page:
            self.__vlog.VLOG('failed to scrap class page')
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
            self.__vlog.VLOG('scrap tape: {stock_code} ({stock_name})'.format( \
                                                                       stock_code = stock_code, \
                                                                       stock_name = tape_item[1][_NAME_KEY]))
            # get link new lib
            if datalib.LINK_FEATURE not in tape_item[1]:
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
                self.__vlog.VLOG('scrap stock: {stock_code} ({stock_name}) ({num}/{all_num})'.format( \
                                                                                              stock_code = stock_code, \
                                                                                              stock_name = stock_item[1][_NAME_KEY], \
                                                                                              num = stock_num, \
                                                                                              all_num = len(class_data)))
                # get link new lib
                if datalib.LINK_FEATURE not in stock_item[1] or \
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

# training file
_TRAINING_DIR = './datalib/crf/'
_DEFAULT_FILE = 'crf_train_'

# data process class
class StockMarketData(object):
    # public
    #   process_market_data  # main function
    #   get_ad_ratios
    # private

    def __init__(self, vlog = 0):
        self.__vlog = log.VLOG(vlog)
        self.__data_lib_file = './datalib/stock_list.lib'
        self.__disable_controler = True
        self.__stock_market_lib = datalib.DataLib(self.__data_lib_file, self.__disable_controler)
        self.__stock_market_lib.load_data_lib()
        self.__stock_market_class = [_ZS_CLASS]  # _ZS_CLASS, _SH_CLASS , _SZ_CLASS, _CY_CLASS]
        self.__crf_file = _TRAINING_DIR + _DEFAULT_FILE + 'all.train'

    # main function
    def process_market_data(self):
        data = self.__stock_market_lib.get_data()
        with tools.open_file(self.__crf_file) as fp:
            for stock_class in self.__stock_market_class:
                class_data = data[stock_class]
                for stock_item in class_data.items():
                    self.__vlog.VLOG('process {} data'.format(stock_item[0]))
                    if datalib.LINK_FEATURE not in stock_item[1] or \
                       stock_item[1][datalib.LINK_FEATURE] == None:
                        self.__vlog.VLOG('data empty, try next one')
                    else:
                        lstock_code = stock_item[1][datalib.LINK_FEATURE].split('/')[-1].split('.')[0]
                        stock_data = stock.StockData(lstock_code, fp = fp)
                    stock_data.display_data()
                    fp.writelines('\n')
                break  # TODO

    # get ad ratios of all stock and sort
    def get_ad_ratios(self):
        stock_ad_ratio = dict()
        stock_market_class = [_SH_CLASS, _SZ_CLASS, _CY_CLASS]
        data = self.__stock_market_lib.get_data()
        for stock_class in stock_market_class:
            class_data = data[stock_class]
            num = 0
            for stock_item in class_data.items():
                num += 1
                self.__vlog.VLOG('process {0} data {1}/{2}'.format(stock_item[0], num, len(class_data)))
                if datalib.LINK_FEATURE not in stock_item[1] or \
                   stock_item[1][datalib.LINK_FEATURE] == None:
                    self.__vlog.VLOG('data empty, try next one')
                else:
                    lstock_code = stock_item[1][datalib.LINK_FEATURE].split('/')[-1].split('.')[0]
                    stock_data = stock.StockData(lstock_code)
                    stock_ad_ratio[lstock_code] = dict()
                    stock_ad_ratio[lstock_code]['6'] = stock_data.get_ad_ratio('2012.01.01')
                    stock_ad_ratio[lstock_code]['5'] = stock_data.get_ad_ratio('2013.01.01')
                    stock_ad_ratio[lstock_code]['4'] = stock_data.get_ad_ratio('2014.01.01')
                    stock_ad_ratio[lstock_code]['3'] = stock_data.get_ad_ratio('2015.01.01')
                    stock_ad_ratio[lstock_code]['2'] = stock_data.get_ad_ratio('2016.01.01')
                    stock_ad_ratio[lstock_code]['1'] = stock_data.get_ad_ratio('2017.01.01')
                    stock_ad_ratio[lstock_code]['3m'] = stock_data.get_ad_ratio('2017.06.01')

        with open('ads', 'w') as fp:
            range_list = ['3m', '1', '2', '3', '4', '5', '6']
            for stock_id in stock_ad_ratio.items():
                strs = stock_id[0]
                for ranges in range_list:
                    strs += '\t%f' % stock_id[1][ranges]
                fp.writelines('%s\n' % strs)
