#!/usr/bin/env python
# coding=utf-8
'''Module for stock process data

Magtroid @ 2017-09-05 10:25
monitor stock and process
'''

# import library
import controler
import common
import copy
import datalib
import log
import proxypool
import re
import stock_market
import tools

# const define
_URL_KEY = 'url'

_STATUS_ALIVE = 'alive'
_STATUS_DEAD = 'dead'

_LAST_TIME = 'last_time'
_LAST_TRANS = 'last_trans'

_DATE_KEY = 'date'
_CASH_KEY = 'cash'
_PROPERTY_KEY = 'property'
_STOCK_KEY = 'stock'
_ACTION_KEY = 'action'

_STOCK_ID_KEY = 'ID'
_STOCK_NUM_KEY = 'number'
_STOCK_PRICE_KEY = 'price'
_STOCK_PCOST_KEY = 'pcost'

_SERVICE_CHARGE_SELL = 1.75
_SERVICE_CHARGE_BUY = 0.75

# main class
class StockMonitor(object):
    # public
    #   stock_monitor  # main function
    # private
    #   __init_stock_list
    #   __update_property_lib
    #   __get_lib_date_range
    #   __commond_control
    #   __process_system_commond
    #   __change_cash
    #   __change_property
    #   __in_cash
    #   __out_cash
    #   __buy_stock
    #   __sell_stock
    #   __new_stock
    #   __get_property_stock
    #   __property_display
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
        self.__disable_controler = False
        self.__property_lib = datalib.DataLib(self.__data_lib_file, self.__disable_controler, vlog = vlog)
        self.__property_lib.load_data_lib()
        self.__today = tools.date_list_to_str(tools.get_date())
        self.__start_date = ''
        self.__end_date = ''
        self.__get_lib_date_range()
        self.__update_property_lib()
        self.__get_page_type = common.URL_WRITE
        self.__url = 'http://api.finance.ifeng.com/amin/?code='
        self.__type = '&type=now'
        self.__max_stock_monitor = 4
        self.__system_commond = ['quit', 'q', 'Q', 'buy', 'sell', 'in', 'out', 'show']
        self.__property = self.__property_lib.get_data(datalib.form_lkey([datalib.DATA_KEY, self.__today, _PROPERTY_KEY]))
        self.__stock_map_list = dict()
        self.__init_stock_map_list()

        self.__stock_list = dict()  # TODO load stock list from datalib
        self.__init_stock_list()
        self.__status = _STATUS_ALIVE

    # monitor stock and property
    def stock_monitor(self):
        while self.__status == _STATUS_ALIVE:
            self.__commond_control()
            self.__display_price()
        self.__write_data_lib()
        self.__vlog.VLOG('done monitor')

    # stock list initial
    def __init_stock_list(self):
        property_data = self.__property_lib.get_data()[self.__today]
        if _STOCK_KEY in property_data:
            stocks = property_data[_STOCK_KEY]
            for item in stocks.items():
                stock = self.__new_stock(item[0])
                self.__stock_list[item[0]] = stock

    # make a stock map list between name and id
    def __init_stock_map_list(self):
        stock_market_lib = stock_market.StockMarket()
        self.__stock_map_list = stock_market_lib.get_stock_map_list()

    # add today lib if a new day, copy last day to new day
    def __update_property_lib(self):
        data = self.__property_lib.get_data()
        if self.__today not in data:
            property_unit = dict()
            if self.__end_date == '':
                property_unit[_CASH_KEY] = 0
                property_unit[_PROPERTY_KEY] = 0
            else:
                property_unit = copy.deepcopy(data[self.__end_date])
            property_unit[_DATE_KEY] = self.__today
            self.__property_lib.insert_data(common.EMPTY_KEY, property_unit, _DATE_KEY)

    # get date lib range to get last day
    def __get_lib_date_range(self):
        for key in self.__property_lib.get_data().keys():
            if key == self.__today:
                continue
            if self.__start_date == '':
                self.__start_date = key
            if self.__end_date == '':
                self.__end_date = key
            if tools.date_compare(key, self.__end_date) == tools.LARGER:
                self.__end_date = key
            if tools.date_compare(key, self.__start_date) == tools.LESS:
                self.__start_date = key

    # receive commond and control
    def __commond_control(self):
        commond = tools.kbhit()
        if commond:
            print commond
            if commond in self.__system_commond:
                self.__process_system_commond(commond)
            elif commond in self.__stock_list:
                del self.__stock_list[commond]
            elif len(self.__stock_list) >= self.__max_stock_monitor:
                self.__vlog.VLOG("full stocks")
            elif commond in self.__stock_map_list:
                stock_id = self.__stock_map_list[commond]
                stock = self.__new_stock(stock_id)
                self.__stock_list[stock_id] = stock
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
            self.__property_display()

    # change cash by number of positive and negative
    def __change_cash(self, number):
        cash_lkey = datalib.form_lkey([datalib.DATA_KEY, self.__today, _CASH_KEY])
        self.__property_lib.increase_data(cash_lkey, float(number))

    # change cash by number of positive and negative
    def __change_property(self, number):
        property_lkey = datalib.form_lkey([datalib.DATA_KEY, self.__today, _PROPERTY_KEY])
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
        if self.__property_lib.get_data(datalib.form_lkey([datalib.DATA_KEY, self.__today, _CASH_KEY])) < float(number):
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
        if stock_list[0] in self.__stock_map_list:
            stock_list[0] = self.__stock_map_list[stock_list[0]]
        else:
            url = self.__url + stock_list[0] + self.__type
            if not self.__proxy_pool.get_page(url):
                self.__vlog.VLOG('error stock id {0}'.format(stock_list[0]))
                return
        if re.match('^\d+\.\d+$', stock_list[1]) and re.match('^\d+$', stock_list[2]):
            price = float(stock_list[1])
            number = int(stock_list[2])
            property_status = self.__property_lib.get_data()[self.__today]
            if property_status[_CASH_KEY] < price * number:
                self.__vlog.VLOG('not enough money')
                return
            else:
                stock_data = self.__get_property_stock()
                if stock_list[0] in stock_data:
                    cstock = stock_data[stock_list[0]]
                    pcost = cstock[_STOCK_PCOST_KEY] * cstock[_STOCK_NUM_KEY]
                    pnumber = cstock[_STOCK_NUM_KEY] + number
                    pcost += price * number
                    pcost = pcost / pnumber
                    pcost_lkey = datalib.form_lkey([datalib.DATA_KEY, self.__today, _STOCK_KEY, stock_list[0], _STOCK_PCOST_KEY])
                    num_lkey = datalib.form_lkey([datalib.DATA_KEY, self.__today, _STOCK_KEY, stock_list[0], _STOCK_NUM_KEY])
                    self.__property_lib.set_data(pcost_lkey, pcost)
                    self.__property_lib.increase_data(num_lkey, number)
                else:
                    stock = dict()
                    stock[_STOCK_ID_KEY] = stock_list[0]
                    stock[_STOCK_PCOST_KEY] = price
                    stock[_STOCK_NUM_KEY] = number
                    stock_lkey = datalib.form_lkey([datalib.DATA_KEY, self.__today, _STOCK_KEY, stock[_STOCK_ID_KEY]])
                    self.__property_lib.set_data(stock_lkey, stock)
                    self.__stock_list[stock_list[0]] = self.__new_stock(stock_list[0])
                value = price * number
                service_charge = value * _SERVICE_CHARGE_BUY / 1000
                self.__change_cash(-value)
                self.__change_cash(-service_charge)
                self.__vlog.VLOG('service charge: {0}'.format(service_charge))
        else:
            self.__vlog.VLOG('error number {0} {1}'.format(stock_list[1], stock_list[2]))

    # sell stock
    def __sell_stock(self):
        self.__vlog.VLOG('insert stock id price number')
        stock_list = tools.stdin().split()
        if len(stock_list) != 3:
            self.__vlog.VLOG('error format')
            return
        if stock_list[0] in self.__stock_map_list:
            stock_list[0] = self.__stock_map_list[stock_list[0]]
        stock_data = self.__get_property_stock()
        if stock_list[0] in stock_data:
            cstock = stock_data[stock_list[0]]
            if re.match('^\d+\.\d+$', stock_list[1]) and re.match('^\d+$', stock_list[2]):
                price = float(stock_list[1])
                number = int(stock_list[2])
                if cstock[_STOCK_NUM_KEY] < number:
                    self.__vlog.VLOG('not enough number (has {0})'.format(cstock[_STOCK_NUM_KEY]))
                    return
                if cstock[_STOCK_NUM_KEY] == number:
                    self.__property_lib.delete_data(datalib.form_lkey([self.__today, _STOCK_KEY, stock_list[0]]))
                else:
                    self.__property_lib.decrease_data(datalib.form_lkey([datalib.DATA_KEY, self.__today, _STOCK_KEY, stock_list[0], _STOCK_NUM_KEY]), number)
                value = number * price
                service_charge = value * _SERVICE_CHARGE_SELL / 1000
                self.__change_cash(value)
                self.__change_cash(-service_charge)
                self.__vlog.VLOG('service charge: {0}'.format(service_charge))
        else:
            self.__vlog.VLOG('no such stock {0}'.format(stock_list[0]))

    # create a new stock to monitor
    def __new_stock(self, stock_id):
        stock = dict()
        stock[_URL_KEY] = self.__url + stock_id + self.__type
        stock[_LAST_TIME] = ''
        stock[_LAST_TRANS] = ''
        return stock

    # get property stock list
    def __get_property_stock(self):
        property_data = self.__property_lib.get_data()[self.__today]
        if _STOCK_KEY in property_data:
            return property_data[_STOCK_KEY]
        else:
            return dict()

    # display property
    def __property_display(self):
        current_property = self.__property_lib.get_data(datalib.form_lkey([datalib.DATA_KEY, self.__today, _PROPERTY_KEY]))
        if self.__end_date == '':
            last_property = current_property
        else:
            last_property = self.__property_lib.get_data(datalib.form_lkey([datalib.DATA_KEY, self.__end_date, _PROPERTY_KEY]))
        self.__vlog.VLOG('property: {0:9.2f} profit_today: {1:8.2f} ratio: {2:-6.2f}%'.format(current_property, current_property - last_property, \
                                                                                              (current_property - last_property) / last_property * 100))
        self.__vlog.VLOG('    cash: {:9.2f}'.format(self.__property_lib.get_data(datalib.form_lkey([datalib.DATA_KEY, self.__today, _CASH_KEY]))))
        stock_data = self.__get_property_stock()
        for stock in stock_data.items():
            self.__vlog.VLOG('   stock: {0} price: {1:-6.2f} number: {2:-6} value: {3:-10.2f} pcost: {4:-5.2f} ratio: {5:-6.2f}%'.format( \
                             stock[1][_STOCK_ID_KEY], stock[1][_STOCK_PRICE_KEY], \
                             stock[1][_STOCK_NUM_KEY], stock[1][_STOCK_PRICE_KEY] * stock[1][_STOCK_NUM_KEY], \
                             stock[1][_STOCK_PCOST_KEY], \
                             (stock[1][_STOCK_PRICE_KEY] / stock[1][_STOCK_PCOST_KEY] - 1) * 100))

    # display each stock price
    def __display_price(self):
        stocks_price = tools.get_time_str(tools.TIME_HOUR, tools.TIME_SECOND, ':')
        property_status = self.__property_lib.get_data()[self.__today]
        total_property = property_status[_CASH_KEY]
        stock_lib = dict()
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
                self.__property_lib.set_data(datalib.form_lkey([datalib.DATA_KEY, self.__today, _STOCK_KEY, \
                                                                stock_item[0], _STOCK_PRICE_KEY]), float(price[2]))

        self.__property_lib.set_data(datalib.form_lkey([datalib.DATA_KEY, self.__today, _PROPERTY_KEY]), total_property)
        self.__vlog.VLOG(stocks_price)
        tools.sleep(3.2)

    # write data lib
    def __write_data_lib(self):
        self.__property_lib.write_data_lib()
        self.__proxy_pool.write_data_lib()
