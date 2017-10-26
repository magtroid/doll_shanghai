#!/usr/bin/env python
# coding=utf-8
'''Module for stock process data

Magtroid @ 2017-09-05 10:25
monitor stock and process
'''

# import library
import canvas
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

_SLEEP_TIME = 3.2

_STATUS_ALIVE = 'alive'
_STATUS_DEAD = 'dead'

_LAST_TIME = 'last_time'
_LAST_PRICE = 'last_price'
_LAST_ADR = 'last_adr'
_LAST_TRANS = 'last_trans'
_STOCK_HISTORY_MAX = 15

_DATE_KEY = 'date'
_CASH_KEY = 'cash'
_PROPERTY_KEY = 'property'
_STOCK_KEY = 'stock'
_ACTION_KEY = 'action'

_ACTION_BUY = 'buy'
_ACTION_SELL = 'sell'
_ACTION_ACTION_KEY = 'action'
_ACTION_STOCK_KEY = 'stock'
_ACTION_PRICE_KEY = 'price'
_ACTION_NUMBER_KEY = 'number'
_ACTION_SERVICE_KEY = 'number'

_STOCK_ID_KEY = 'ID'
_STOCK_NUM_KEY = 'number'
_STOCK_PRICE_KEY = 'price'
_STOCK_PCOST_KEY = 'pcost'

_SERVICE_CHARGE_SELL = 1.75
_SERVICE_CHARGE_BUY = 0.75

_DISPLAY_NUM_PER_LINE = 4
# display const index
_PROPERTY_INDEX = 0
_DETAIL_INDEX = 1

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
    #   __set_detail_list
    #   __show_detail
    #   __new_stock
    #   __new_action
    #   __stock_history_append
    #   __get_property_stock
    #   __get_virtual_property
    #   __get_last_virtual_property
    #   __property_display
    #   __display_price
    #   __display_market
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
        self.__canvas = canvas.CANVAS(vlog = vlog)
        self.__start_date = ''
        self.__end_date = ''
        self.__get_lib_date_range()
        self.__update_property_lib()
        self.__get_page_type = common.URL_WRITE
        self.__url = 'http://api.finance.ifeng.com/amin/?code='
        self.__type = '&type=now'
        self.__max_stock_monitor = 8
        self.__system_commond = ['quit', 'q', 'Q', 'buy', 'sell', 'in', 'out', 'd', 'detail', 'show']
        self.__property = self.__property_lib.get_data(datalib.form_lkey([datalib.DATA_KEY, self.__today, _PROPERTY_KEY]))
        self.__stock_map_list = dict()
        self.__init_stock_map_list()
        self.__display_feat = [False, '']  # 1:property 2:detail_stock
        self.__display_feat_len = 58

        self.__stock_list = dict()  # TODO load stock list from datalib
        self.__init_stock_list()
        self.__status = _STATUS_ALIVE

    # monitor stock and property
    def stock_monitor(self):
        while self.__status == _STATUS_ALIVE:
            self.__commond_control()
            self.__display_market()
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
            if _ACTION_KEY in property_unit:
                del property_unit[_ACTION_KEY]
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
            commond_list = commond.split()
            if len(commond_list) != 1:
                commond = commond_list[0]
                argv = commond_list[1:]
            else:
                argv = []
            if commond in self.__system_commond:
                self.__process_system_commond(commond, argv)
            elif commond in self.__stock_map_list:
                commond = self.__stock_map_list[commond]
                if commond in self.__stock_list:
                    if commond == self.__display_feat[_DETAIL_INDEX]:
                        self.__display_feat[_DETAIL_INDEX] = ''
                    del self.__stock_list[commond]
                else:
                    stock = self.__new_stock(commond)
                    if len(self.__stock_list) < self.__max_stock_monitor:
                        self.__stock_list[commond] = stock
            elif commond in self.__stock_list:
                if commond == self.__display_feat[_DETAIL_INDEX]:
                    self.__display_feat[_DETAIL_INDEX] = ''
                del self.__stock_list[commond]
            else:
                stock = self.__new_stock(commond)
                if len(self.__stock_list) < self.__max_stock_monitor and \
                   self.__proxy_pool.get_page(stock[_URL_KEY]):
                    self.__stock_list[commond] = stock

    # process commond in system_commond
    def __process_system_commond(self, commond, argv = None):
        if commond == 'q' or commond == 'Q' or commond == 'quit':
            self.__status = _STATUS_DEAD
        elif commond == 'in':
            for money in argv:
                self.__in_cash(money)
        elif commond == 'out':
            for money in argv:
                self.__out_cash(money)
        elif commond == 'buy':
            self.__buy_stock()
        elif commond == 'sell':
            self.__sell_stock()
        elif commond == 'detail' or commond == 'd':
            stock_id = None if len(argv) == 0 else argv[0]
            self.__set_detail_list(stock_id)
        elif commond == 'show':
            self.__display_feat[_PROPERTY_INDEX] ^= True

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
                action = self.__new_action(_ACTION_BUY, stock_list[0], price, number, service_charge)
                action_lkey = datalib.form_lkey([datalib.DATA_KEY, self.__today, _ACTION_KEY, tools.get_time_str(tools.TIME_HOUR, tools.TIME_SECOND, '.')])
                self.__property_lib.set_data(action_lkey, action)
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

                action = self.__new_action(_ACTION_SELL, stock_list[0], price, number, service_charge)
                action_lkey = datalib.form_lkey([datalib.DATA_KEY, self.__today, _ACTION_KEY, tools.get_time_str(tools.TIME_HOUR, tools.TIME_SECOND, '.')])
                self.__property_lib.set_data(action_lkey, action)
        else:
            self.__vlog.VLOG('no such stock {0}'.format(stock_list[0]))

    # set detail stock and check legal
    def __set_detail_list(self, stock_id = None):
        if stock_id is None:
            self.__vlog.VLOG('insert stock id')
            stock_id = tools.stdin()
        if stock_id in self.__stock_map_list:
            stock_id = self.__stock_map_list[stock_id]
        elif re.match('\d', stock_id):
            stock_id = int(stock_id) - 1
            if stock_id >= 0 and stock_id < len(self.__stock_list):
                stock_id = self.__stock_list.keys()[stock_id]
        if stock_id in self.__stock_list:
            if self.__display_feat[_DETAIL_INDEX] == stock_id:
                self.__display_feat[_DETAIL_INDEX] = ''
            else:
                self.__display_feat[_DETAIL_INDEX] = stock_id
        else:
            self.__vlog.VLOG('no such stock {0}'.format(stock_id))

    # show five range detail of target stock
    def __show_detail(self, stock_id):
        if stock_id not in self.__stock_list:
            return
        self.__canvas.paint('-' * self.__display_feat_len, canvas.BACKSPACE)
        history_len = len(self.__stock_list[stock_id][_LAST_TIME])
        for history in range(history_len):
            his_info = '{0:5s}:   {1:3.2f}  {2:>6.2f} {3:10d}'.format(self.__stock_list[stock_id][_LAST_TIME][history], \
                                                                      self.__stock_list[stock_id][_LAST_PRICE][history], \
                                                                      self.__stock_list[stock_id][_LAST_ADR][history], \
                                                                      self.__stock_list[stock_id][_LAST_TRANS][history])
            self.__canvas.paint(his_info, canvas.BACKSPACE)
        self.__canvas.paint('-' * self.__display_feat_len, canvas.BACKSPACE)

        detail_url = ''.join(['https://hq.finance.ifeng.com/q.php?l=', stock_id, ',&f=json;&r=0.9134400947969383&_=1507612356174'])
        response = self.__proxy_pool.get_page(detail_url)
        if len(response) == 0:
            self.__canvas.paint('failed to get detail of stock', canvas.BACKSPACE)
            return
        detail = response.split(',')
        buy_list = detail[11:21]
        sell_list = detail[21:31]
        for stage in range(5):
            self.__canvas.paint('{0:6s}: {1:8d}'.format(sell_list[4 - stage], int(float(sell_list[9 - stage])) / 100), canvas.BACKSPACE)
        self.__canvas.paint('-' * 16, canvas.BACKSPACE)
        for stage in range(5):
            self.__canvas.paint('{0:6s}: {1:8d}'.format(buy_list[stage], int(float(buy_list[5 + stage])) / 100), canvas.BACKSPACE)

    # create a new stock to monitor
    def __new_stock(self, stock_id):
        stock = dict()
        stock[_URL_KEY] = self.__url + stock_id + self.__type
        stock[_LAST_TIME] = []
        stock[_LAST_PRICE] = []
        stock[_LAST_ADR] = []
        stock[_LAST_TRANS] = []
        return stock

    # create a new action
    def __new_action(self, bs, stock_id, price, number, service_charge):
        action = dict()
        action[_ACTION_ACTION_KEY] = bs
        action[_ACTION_STOCK_KEY] = stock_id
        action[_ACTION_PRICE_KEY] = price
        action[_ACTION_NUMBER_KEY] = number
        action[_ACTION_SERVICE_KEY] = service_charge
        return action

    # append story history, del first one if exceed
    def __stock_history_append(self, stock_feat, value):
        stock_feat.append(value)
        if len(stock_feat) > _STOCK_HISTORY_MAX:
            del stock_feat[0]

    # get property stock list
    def __get_property_stock(self):
        property_data = self.__property_lib.get_data()[self.__today]
        if _STOCK_KEY in property_data:
            return property_data[_STOCK_KEY]
        else:
            return dict()

    # get current property of target date, if no actions
    def __get_virtual_property(self, date):
        data = self.__property_lib.get_data()
        virtual_property = 0
        if date in data:
            date_property = data[date]
            virtual_property += date_property[_CASH_KEY]
            if _STOCK_KEY in date_property:
                for stock_item in date_property[_STOCK_KEY].items():
                    url = self.__url + stock_item[0] + self.__type
                    response = self.__proxy_pool.get_page(url)
                    if len(response) == 0:
                        return 0
                    price = re.sub('"', '', response[1:-1].encode('utf-8')).split(',')
                    virtual_property += float(price[2]) * stock_item[1][_STOCK_NUM_KEY]
        return virtual_property

    # get last action property
    def __get_last_virtual_property(self):
        last_virtual_property = 0
        if len(self.__end_date) == 0:
            return last_virtual_property
        last_action_date = self.__end_date
        while tools.date_compare(last_action_date, self.__start_date) != tools.LESS:
            if self.__property_lib.lhas_key(datalib.form_lkey([datalib.DATA_KEY, last_action_date, _ACTION_KEY])):
                last_property_date = tools.get_date(-1, last_action_date, [common.SAT, common.SUN])
                last_virtual_property = self.__get_virtual_property(last_property_date)
                self.__canvas.paint(last_property_date, canvas.BACKSPACE)  # TODO
                self.__canvas.paint(last_virtual_property, canvas.BACKSPACE)  # TODO
                break
            last_action_date = tools.get_date(-1, last_action_date)
        return last_virtual_property

    # display property
    def __property_display(self):
        self.__canvas.paint('-' * self.__display_feat_len, canvas.BACKSPACE)
        current_property = self.__property_lib.get_data(datalib.form_lkey([datalib.DATA_KEY, self.__today, _PROPERTY_KEY]))
        if self.__end_date == '':
            last_property = current_property
        else:
            last_property = self.__property_lib.get_data(datalib.form_lkey([datalib.DATA_KEY, self.__end_date, _PROPERTY_KEY]))
        last_virtual_property = self.__get_last_virtual_property()
        self.__canvas.paint('property: {0:9.2f}  profit_today: {1:8.2f} ratio: {2:-6.2f}%'.format(current_property, current_property - last_property, \
                                                                                                  (current_property - last_property) / last_property * 100), canvas.BACKSPACE)
        if last_virtual_property:
            self.__canvas.paint(' virtual: {0:9.2f} action_profit: {1:8.2f} ratio: {2:-6.2f}%'.format(last_virtual_property, current_property - last_virtual_property, \
                                                                                                      (current_property - last_virtual_property) / last_property * 100), canvas.BACKSPACE)
        self.__canvas.paint('    cash: {:9.2f}'.format(self.__property_lib.get_data(datalib.form_lkey([datalib.DATA_KEY, self.__today, _CASH_KEY]))), canvas.BACKSPACE)
        stock_data = self.__get_property_stock()
        for stock in stock_data.items():
            self.__canvas.paint('   stock: {0} price: {1:-6.2f} number: {2:-6} value: {3:-10.2f} pcost: {4:-5.2f} ratio: {5:-6.2f}%'.format( \
                             stock[1][_STOCK_ID_KEY], stock[1][_STOCK_PRICE_KEY], \
                             stock[1][_STOCK_NUM_KEY], stock[1][_STOCK_PRICE_KEY] * stock[1][_STOCK_NUM_KEY], \
                             stock[1][_STOCK_PCOST_KEY], \
                             (stock[1][_STOCK_PRICE_KEY] / stock[1][_STOCK_PCOST_KEY] - 1) * 100), canvas.BACKSPACE)

    # display each stock price
    def __display_price(self):
        self.__canvas.paint('-' * self.__display_feat_len, canvas.BACKSPACE)
        stocks_price = tools.get_time_str(tools.TIME_HOUR, tools.TIME_SECOND, ':')
        property_status = self.__property_lib.get_data()[self.__today]
        total_property = property_status[_CASH_KEY]
        market_suspended = False
        stock_lib = dict()
        if _STOCK_KEY in property_status:
            stock_lib = property_status[_STOCK_KEY]
        stock_number = 0
        for stock_item in self.__stock_list.items():
            stock_number += 1
            response = self.__proxy_pool.get_page(stock_item[1][_URL_KEY])
            if len(response) == 0:
                market_suspended = True
                if stock_item[0] in stock_lib:
                    total_property += stock_lib[stock_item[0]][_STOCK_PRICE_KEY] * stock_lib[stock_item[0]][_STOCK_NUM_KEY]
                continue
            price = re.sub('"', '', response[1:-1].encode('utf-8')).split(',')
            ctime = re.sub(':\d\d$', '', price[0].split()[1])
            if len(stock_item[1][_LAST_TIME]) == 0 or stock_item[1][_LAST_TIME][-1] != ctime:
                transaction = int(price[6])
                self.__stock_history_append(stock_item[1][_LAST_TIME], ctime)
                self.__stock_history_append(stock_item[1][_LAST_PRICE], float(price[2]))
                self.__stock_history_append(stock_item[1][_LAST_ADR], float(price[3]))
                self.__stock_history_append(stock_item[1][_LAST_TRANS], int(price[6]))
            else:
                transaction = int(price[6]) - stock_item[1][_LAST_TRANS][-1]
                stock_item[1][_LAST_PRICE][-1] = float(price[2])
                stock_item[1][_LAST_ADR][-1] = float(price[3])
                stock_item[1][_LAST_TRANS][-1] = int(price[6])
            if stock_number != 1 and stock_number % _DISPLAY_NUM_PER_LINE == 1:
                stocks_price += '\n        '
            stocks_price += '  |  {stock_id} {price:7.2f} {rate:7.2f} {trans:7d}'.format(stock_id = stock_item[0], \
                                                                                         price = float(price[2]), \
                                                                                         rate = float(price[3]), \
                                                                                         trans = transaction)
            if stock_item[0] in stock_lib:
                total_property += float(price[2]) * stock_lib[stock_item[0]][_STOCK_NUM_KEY]
                self.__property_lib.set_data(datalib.form_lkey([datalib.DATA_KEY, self.__today, _STOCK_KEY, \
                                                                stock_item[0], _STOCK_PRICE_KEY]), float(price[2]))

        if market_suspended:
            self.__canvas.paint('stock market suspended', canvas.BACKSPACE)
            return
        self.__property_lib.set_data(datalib.form_lkey([datalib.DATA_KEY, self.__today, _PROPERTY_KEY]), total_property)
        self.__canvas.paint(stocks_price, canvas.BACKSPACE)

    # display all stock markets
    def __display_market(self):
        self.__canvas.clear()
        if self.__display_feat[_PROPERTY_INDEX]:
            self.__property_display()
        self.__display_price()
        if self.__display_feat[_DETAIL_INDEX] != '':
            self.__show_detail(self.__display_feat[_DETAIL_INDEX])
        self.__canvas.display()
        tools.sleep(_SLEEP_TIME)

    # write data lib
    def __write_data_lib(self):
        self.__property_lib.write_data_lib()
        self.__proxy_pool.write_data_lib()
