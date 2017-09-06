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

_CASH_KEY = 'cash'
_PROPERTY_KEY = 'property'

_STOCK_KEY = 'stock'
_STOCK_ID_KEY = 'ID'
_STOCK_NUM_KEY = 'number'
_STOCK_PCOST_KEY = 'pcost'

# main class
class StockMonitor(object):
    # public
    #   stock_monitor  # main function
    # private
    #   __init_property_lib
    #   __commond_control
    #   __process_system_commond
    #   __change_cash
    #   __change_property
    #   __in_cash
    #   __out_cash
    #   __buy_stock
    #   __sell_stock
    #   __new_stock
    #   __calcu_property
    #   __display_price
    #   __write_data_lib
    
    def __init__(self, vlog = 0, proxy_pool = None):
        self.__vlog = log.VLOG(vlog)
        if proxy_pool == None:
            self.__proxy_pool = proxypool.ProxyPool()
        else:
            self.__proxy_pool = proxy_pool
        self.__proxy_pool.set_threshold(20000)
        self.__data_lib_file = './datalib/property.lib'
        self.__disable_controler = True  # TODO
        self.__property_lib = datalib.DataLib(self.__data_lib_file, self.__disable_controler, vlog = vlog)
        self.__property_lib.load_data_lib()
        self.__init_property_lib()
        self.__get_page_type = common.URL_WRITE
        self.__url = 'http://api.finance.ifeng.com/amin/?code='
        self.__type = '&type=now'
        self.__max_stock_monitor = 4
        self.__system_commond = ['quit', 'q', 'Q', 'buy', 'sell', 'in', 'out', 'show']
        self.__property = self.__property_lib.get_data()[_PROPERTY_KEY]

        self.__stock_list = dict()  # TODO load stock list from datalib
        self.__status = _STATUS_ALIVE

    # monitor stock and property
    def stock_monitor(self):
        while self.__status == _STATUS_ALIVE:
            self.__commond_control()
            self.__display_price()
        self.__write_data_lib()
        self.__vlog.VLOG('done monitor')

    # init lib
    def __init_property_lib(self):
        self.__property_lib.insert_data(common.EMPTY_KEY, 0, _CASH_KEY)
        self.__property_lib.insert_data(common.EMPTY_KEY, 0, _PROPERTY_KEY)

    # receive commond and control
    def __commond_control(self):
        commond = tools.kbhit()
        if commond:
            if commond in self.__system_commond:
                self.__process_system_commond(commond)
            elif commond in self.__stock_list:
                del self.__stock_list[commond]
            elif len(self.__stock_list) >= self.__max_stock_monitor:
                self.__vlog.VLOG("full stocks")
            else:
                stock = self.__new_stock(commond)
                if self.__proxy_pool.get_page(stock[_URL_KEY]):
                    self.__stock_list[commond] = stock

    # process commond in system_commond
    def __process_system_commond(self, commond):
        if commond == 'q' or commond == 'Q' or commond == 'quit':
            self.__status = _STATUS_DEAD
        elif commond == 'in':
            self.__in_cash()
        elif commond == 'out':
            self.__out_cash()
        elif commond == 'buy':
            self.__buy_stock()
        elif commond == 'sell':
            self.__sell_stock()
        elif commond == 'show':
            self.__vlog.VLOG(self.__property_lib.get_data())

    # change cash by number of positive and negative
    def __change_cash(self, number):
        cash_lkey = ''.join([datalib.DATA_KEY, datalib.LIB_CONNECT, _CASH_KEY])
        self.__property_lib.increase_data(cash_lkey, float(number))

    # change cash by number of positive and negative
    def __change_property(self, number):
        property_lkey = ''.join([datalib.DATA_KEY, datalib.LIB_CONNECT, _PROPERTY_KEY])
        self.__property_lib.increase_data(property_lkey, float(number))

    # in cash and add property
    def __in_cash(self, number = None):
        if number is None:
            number = common.NONE
            while not re.match('^\d+(\.\d+)?$', number):
                self.__vlog.VLOG('insert your in number')
                number = tools.stdin()
        self.__change_cash(float(number))
        self.__change_property(float(number))

    # out cash and decrease property
    def __out_cash(self, number = None):
        if number is None:
            number = common.NONE
            while not re.match('^\d+(\.\d+)?$', number):
                self.__vlog.VLOG('insert your in number')
                number = tools.stdin()
        lkey = ''.join([datalib.DATA_KEY, datalib.LIB_CONNECT, _CASH_KEY])
        if self.__property_lib.get_data(lkey) < float(number):
            self.__vlog.VLOG('not enough cash to out')
        else:
            self.__change_cash(-float(number))
            self.__change_property(-float(number))

    # buy stock
    def __buy_stock(self):
        self.__vlog.VLOG('insert stock id price number')
        stock_list = tools.stdin().split()
        if len(stock_list) != 3:
            self.__vlog.VLOG('error format')
            return
        url = self.__url + stock_list[0] + self.__type
        if not self.__proxy_pool.get_page(url):
            self.__vlog.VLOG('error stock id {0}'.format(stock_list[0]))
            return
        if re.match('^\d+\.\d+$', stock_list[1]) and re.match('^\d+$', stock_list[2]):
            price = float(stock_list[1])
            number = int(stock_list[2])
            property_status = self.__property_lib.get_data()
            if property_status[_CASH_KEY] < price * number:
                self.__vlog.VLOG('not enough money')
                return
            else:
                stock = dict()
                stock[_STOCK_ID_KEY] = stock_list[0]
                stock[_STOCK_PCOST_KEY] = price
                stock[_STOCK_NUM_KEY] = number
                self.__property_lib.insert_data(_STOCK_KEY, stock, _STOCK_ID_KEY)
                self.__change_cash(-price * number)
        else:
            self.__vlog.VLOG('error number {0} {1}'.format(stock_list[1], stock_list[2]))
            return
        return

    # sell stock
    def __sell_stock(self):
        return

    # create a new stock to monitor
    def __new_stock(self, stock_id):
        stock = dict()
        stock[_URL_KEY] = self.__url + stock_id + self.__type
        stock[_LAST_TIME] = ''
        stock[_LAST_TRANS] = ''
        return stock

    # caculate property
    def __calcu_property(self):
        property_data = self.__property_lib.get_data()
        total_property = property_data[_CASH_KEY]

    # display each stock price
    def __display_price(self):
        stocks_price = tools.get_time_str(tools.TIME_HOUR, tools.TIME_SECOND, ':')
        property_status = self.__property_lib.get_data()
        total_property = property_status[_CASH_KEY]
        if _STOCK_KEY in property_status:
            stock_lib = property_status[_STOCK_KEY]
        for stock_item in self.__stock_list.items():
            response = self.__proxy_pool.get_page(stock_item[1][_URL_KEY])
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

            if stock_item[0] in stock_lib:
                total_property += float(price[2]) * stock_lib[stock_item[0]][_STOCK_NUM_KEY]

        self.__property_lib.set_data(''.join([datalib.DATA_KEY, datalib.LIB_CONNECT, _PROPERTY_KEY]), total_property)
        self.__vlog.VLOG(stocks_price)
        tools.sleep(3.2)

    # write data lib
    def __write_data_lib(self):
        self.__property_lib.write_data_lib()
        self.__proxy_pool.write_data_lib()
