#!/usr/bin/env python
# coding=utf-8
'''Module for stock process data

Magtroid @ 2017-09-05 10:25
monitor stock and process
'''

# import library
import time
import copy
import re

import canvas
import controler
import common
import datalib
import log
import malarm
import mio
import proxypool
import stock_market
import tools

# const define
_URL_KEY = 'url'
_NAME_KEY = 'stock_name'
_STOCK_NAME_LEN = 4

_SLEEP_TIME = 3.0
_REFRESH_STEP = 0.1

_STATUS_ALIVE = 'alive'
_STATUS_DEAD = 'dead'

_LIST_ID_OFF = 0
_LIST_DATA_OFF = 1
_LAST_TIME = 'last_time'
_LAST_PRICE = 'last_price'
_LAST_ADR = 'last_adr'
_LAST_TRANS = 'last_trans'
_LAST_CLOSE = 'last_close'
_STOCK_HISTORY_MAX = 15

_DATE_KEY = 'date'
_CASH_KEY = 'cash'
_PROPERTY_KEY = 'property'
_STOCK_KEY = 'stock'
_ACTION_KEY = 'action'

_VIEW_MODEL = 'VIEW MODEL'
_COMMAND_MODEL = 'COMMAND MODEL'

_ACTION_BUY = 'buy'
_ACTION_SELL = 'sell'
_ACTION_ACTION_KEY = 'action'
_ACTION_STOCK_KEY = 'stock'
_ACTION_PRICE_KEY = 'price'
_ACTION_NUMBER_KEY = 'number'
_ACTION_SERVICE_KEY = 'service'

_STOCK_ID_KEY = 'ID'
_STOCK_NUM_KEY = 'number'
_STOCK_PRICE_KEY = 'price'
_STOCK_PCOST_KEY = 'pcost'

_SERVICE_CHARGE_SELL = 1.75
_SERVICE_CHARGE_BUY = 0.75

_DISPLAY_NUM_PER_LINE = 4
_STOCK_HEAD_BUF = 2
# display const index
_PROPERTY_INDEX = 0
_DETAIL_INDEX = 1

# canvas area list
_AREA_Y_KEY = 0
_AREA_S_KEY = 1
_PROPERTY = 'property'
_DETAIL = 'detail'
# area structure list
_PROPERTY_STRUCT = [18, [0, 10, 100]]
_DETAIL_STRUCT = {1 : [30, [  0, 30, 50]],
                  2 : [30, [ 50, 30, 50]],
                  3 : [30, [100, 30, 50]],
                  } 

_SELECT_SIGN = '@'
_SELECT_ID_KEY = 'stock_id'

# main class
class StockMonitor(object):
    # public
    #   stock_monitor  # main function
    # private
    #   __init_stock_list
    #   __insert_stock_list
    #   __del_stock_list
    #   __init_canvas_area
    #   __update_property_lib
    #   __get_lib_date_range
    #   __command_control
    #   __process_system_command
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
    #   __stop_alarm
    #   __display_cursor_refresh
    #   __display_price
    #   __display_market
    #   __write_data_lib
    
    def __init__(self, proxy_pool = None):
        if proxy_pool == None:
            self.__proxy_pool = proxypool.ProxyPool()
        else:
            self.__proxy_pool = proxy_pool
        self.__proxy_pool.set_threshold(20000)
        self.__data_lib_file = './datalib/property.lib'
        self.__select_lib_file = './datalib/select_list.lib'
        self.__disable_controler = False
        self.__property_lib = datalib.DataLib(self.__data_lib_file, self.__disable_controler)
        self.__property_lib.load_data_lib()
        self.__select_lib = datalib.DataLib(self.__select_lib_file, self.__disable_controler)
        self.__select_lib.load_data_lib()
        self.__today = tools.date_list_to_str(tools.get_date())
        self.__canvas = canvas.CANVAS()
        self.__init_canvas_area()
        self.__start_date = ''
        self.__end_date = ''
        self.__get_lib_date_range()
        self.__update_property_lib()
        self.__get_page_type = common.URL_WRITE
        self.__url = 'http://api.finance.ifeng.com/amin/?code='
        self.__type = '&type=now'
        self.__max_stock_monitor = 15
        self.__system_command = ['quit', 'S', 'q', 'Q', 'buy', 'sell', 'in', 'out', 'd', 'detail', 'show']
        self.__view_command = ['S', common.UP_KEY, common.DOWN_KEY, '+', '-', '\n']
        self.__view_model = True
        self.__stock_map_list = dict()
        self.__init_stock_map_list()
        self.__display_feat = [False, dict()]  # 1:property 2:detail_stock
        self.__display_feat_len = 58
        self.__alarm = []

        self.__stock_list = dict()  # TODO load stock list from datalib  value is [id, stock]
        self.__init_stock_list()
        self.__stock_list_cursor = 0
        self.__stock_list_offset = 0
        self.__status = _STATUS_ALIVE

    # monitor stock and property
    def stock_monitor(self):
        self.__alarm.append(malarm.MAlarm(_SLEEP_TIME, func = self.__command_control, rtime = _REFRESH_STEP))
        self.__alarm.append(malarm.MAlarm(_SLEEP_TIME, func = self.__display_market, rtime = _SLEEP_TIME))
        while self.__status == _STATUS_ALIVE:
            time.sleep(_REFRESH_STEP)
        self.__stop_alarm()
        self.__write_data_lib()
        log.VLOG('done monitor')

    # stock list initial
    def __init_stock_list(self):
        property_data = self.__property_lib.get_data()[self.__today]
        if _STOCK_KEY in property_data:
            stocks = property_data[_STOCK_KEY]
            for item in stocks.items():
                self.__insert_stock_list(item[0])
        select_list = self.__select_lib.get_data()
        for iselect in sorted(select_list.items(), key = lambda d:d[0]):
            self.__insert_stock_list(iselect[0])

    def __insert_stock_list(self, stock_id, check = False):
        if len(self.__stock_list) < self.__max_stock_monitor and stock_id not in self.__stock_list:
            stock = self.__new_stock(stock_id)
            if not check or self.__proxy_pool.get_page(stock[_URL_KEY]):
                self.__stock_list[stock_id] = [len(self.__stock_list), stock]

    def __del_stock_list(self, stock_id):
        if stock_id in self.__stock_list:
            stock_list_id = self.__stock_list[stock_id][_LIST_ID_OFF]
            del self.__stock_list[stock_id]
            for istock, stock_data in self.__stock_list.items():
                if stock_data[_LIST_ID_OFF] >= stock_list_id:
                    self.__stock_list[istock][_LIST_ID_OFF] -= 1

    def __init_canvas_area(self):
        self.__canvas.new_area(_PROPERTY_STRUCT[_AREA_S_KEY:], line = _PROPERTY_STRUCT[_AREA_Y_KEY], name = _PROPERTY)

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

    # receive command and control
    def __command_control(self):
        if self.__view_model:
            command = mio.kbhit(refresh_times = 10)
            if command in self.__view_command:
                self.__process_view_command(command)
                self.__canvas.display()
        else:
            command = mio.kbhit(one_hit = False).strip()
            if command:
                command_list = command.split()
                if len(command_list) != 1:
                    command = command_list[0]
                    argv = command_list[1:]
                else:
                    argv = []
                if command in self.__system_command:
                    self.__process_system_command(command, argv)
                elif command in self.__stock_map_list:
                    command = self.__stock_map_list[command]
                    if command in self.__stock_list:
                        if command in self.__display_feat[_DETAIL_INDEX]:
                            del self.__display_feat[_DETAIL_INDEX][command]
                            self.__canvas.del_area(command)
                        self.__del_stock_list(command)
                    else:
                        self.__insert_stock_list(command)
                elif command in self.__stock_list:
                    if command in self.__display_feat[_DETAIL_INDEX]:
                        del self.__display_feat[_DETAIL_INDEX][command]
                        self.__canvas.del_area(command)
                    self.__del_stock_list(command)
                else:
                    self.__insert_stock_list(command, check = True)

    # process view command in view model
    def __process_view_command(self, command):
        if command == 'S':
            self.__view_model = False
        elif command == common.UP_KEY:
            if self.__stock_list_cursor > 0:
                self.__stock_list_cursor -= 1
                self.__display_cursor_refresh(self.__stock_list_cursor + 1, self.__stock_list_cursor)
        elif command == common.DOWN_KEY:
            if self.__stock_list_cursor < len(self.__stock_list) - 1:
                self.__stock_list_cursor += 1
                self.__display_cursor_refresh(self.__stock_list_cursor - 1, self.__stock_list_cursor)
        elif command == '+':
            stock_id = sorted(self.__stock_list.items(), key = lambda d:d[1][_LIST_ID_OFF])[self.__stock_list_cursor][0]
            select_stock = dict()
            select_stock[_SELECT_ID_KEY] = stock_id
            self.__select_lib.insert_data(common.EMPTY_KEY, select_stock, _SELECT_ID_KEY)
        elif command == '-':
            stock_id = sorted(self.__stock_list.items(), key = lambda d:d[1][_LIST_ID_OFF])[self.__stock_list_cursor][0]
            self.__select_lib.delete_data(datalib.form_lkey([stock_id]))
        elif command == '\n':
            stock_id = sorted(self.__stock_list.items(), key = lambda d:d[1][_LIST_ID_OFF])[self.__stock_list_cursor][0]
            self.__set_detail_list(stock_id)

    # process command in system_command
    def __process_system_command(self, command, argv = None):
        if command == 'q' or command == 'Q' or command == 'quit':
            self.__status = _STATUS_DEAD
        elif command == 'S':
            self.__view_model = True
        elif command == 'in':
            for money in argv:
                self.__in_cash(money)
        elif command == 'out':
            for money in argv:
                self.__out_cash(money)
        elif command == 'buy':
            self.__buy_stock()
        elif command == 'sell':
            self.__sell_stock()
        elif command == 'detail' or command == 'd':
            stock_id = None if len(argv) == 0 else argv[0]
            self.__set_detail_list(stock_id)
        elif command == 'show':
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
                log.VLOG('insert your in number')
                number = mio.stdin()
        self.__change_cash(float(number))
        self.__change_property(float(number))

    # out cash and decrease property
    def __out_cash(self, number = None):
        if number is None:
            number = common.NONE
            while not re.match('^\d+(\.\d+)?$', number):
                log.VLOG('insert your in number')
                number = mio.stdin()
        if self.__property_lib.get_data(datalib.form_lkey([datalib.DATA_KEY, self.__today, _CASH_KEY])) < float(number):
            log.VLOG('not enough cash to out')
        else:
            self.__change_cash(-float(number))
            self.__change_property(-float(number))

    # buy stock
    def __buy_stock(self):
        log.VLOG('insert stock id price number')
        stock_list = mio.stdin().split()
        if len(stock_list) != 3:
            log.VLOG('error format')
            return
        if stock_list[0] in self.__stock_map_list:
            stock_list[0] = self.__stock_map_list[stock_list[0]]
        else:
            url = self.__url + stock_list[0] + self.__type
            if not self.__proxy_pool.get_page(url):
                log.VLOG('error stock id {0}'.format(stock_list[0]))
                return
        if re.match('^\d+\.\d+$', stock_list[1]) and re.match('^\d+$', stock_list[2]):
            price = float(stock_list[1])
            number = int(stock_list[2])
            property_status = self.__property_lib.get_data()[self.__today]
            if property_status[_CASH_KEY] < price * number:
                log.VLOG('not enough money')
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
                    self.__insert_stock_list(stock_list[0])
                value = price * number
                service_charge = value * _SERVICE_CHARGE_BUY / 1000
                action = self.__new_action(_ACTION_BUY, stock_list[0], price, number, service_charge)
                action_lkey = datalib.form_lkey([datalib.DATA_KEY, self.__today, _ACTION_KEY, tools.get_time_str(tools.TIME_HOUR, tools.TIME_SECOND, '.')])
                self.__property_lib.set_data(action_lkey, action)
                self.__change_cash(-value)
                self.__change_cash(-service_charge)
                log.VLOG('service charge: {0}'.format(service_charge))
        else:
            log.VLOG('error number {0} {1}'.format(stock_list[1], stock_list[2]))

    # sell stock
    def __sell_stock(self):
        log.VLOG('insert stock id price number')
        stock_list = mio.stdin().split()
        if len(stock_list) != 3:
            log.VLOG('error format')
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
                    log.VLOG('not enough number (has {0})'.format(cstock[_STOCK_NUM_KEY]))
                    return
                if cstock[_STOCK_NUM_KEY] == number:
                    self.__property_lib.delete_data(datalib.form_lkey([self.__today, _STOCK_KEY, stock_list[0]]))
                else:
                    self.__property_lib.decrease_data(datalib.form_lkey([datalib.DATA_KEY, self.__today, _STOCK_KEY, stock_list[0], _STOCK_NUM_KEY]), number)
                value = number * price
                service_charge = value * _SERVICE_CHARGE_SELL / 1000
                self.__change_cash(value)
                self.__change_cash(-service_charge)
                log.VLOG('service charge: {0}'.format(service_charge))

                action = self.__new_action(_ACTION_SELL, stock_list[0], price, number, service_charge)
                action_lkey = datalib.form_lkey([datalib.DATA_KEY, self.__today, _ACTION_KEY, tools.get_time_str(tools.TIME_HOUR, tools.TIME_SECOND, '.')])
                self.__property_lib.set_data(action_lkey, action)
        else:
            log.VLOG('no such stock {0}'.format(stock_list[0]))

    # set detail stock and check legal
    def __set_detail_list(self, stock_id = None):
        if stock_id is None:
            log.VLOG('insert stock id')
            stock_id = mio.stdin()
        if stock_id in self.__stock_map_list:
            stock_id = self.__stock_map_list[stock_id]
        elif re.match('\d', stock_id):
            stock_id = int(stock_id) - 1
            if stock_id >= 0 and stock_id < len(self.__stock_list):
                stock_id = list(self.__stock_list.keys())[stock_id]
        if stock_id in self.__stock_list:
            if stock_id in self.__display_feat[_DETAIL_INDEX]:
                del self.__display_feat[_DETAIL_INDEX][stock_id]
                self.__canvas.del_area(stock_id)
            else:
                for detail_key, detail_struct in _DETAIL_STRUCT.items():
                    if detail_key not in self.__display_feat[_DETAIL_INDEX].values():
                        self.__display_feat[_DETAIL_INDEX][stock_id] = detail_key
                        self.__canvas.new_area(detail_struct[_AREA_S_KEY:], line = detail_struct[_AREA_Y_KEY], name = stock_id)
                        break
                else:
                    log.VLOG('full detail list')
        else:
            log.VLOG('no such stock {0}'.format(stock_id))

    # show five range detail of target stock
    def __show_detail(self, stock_id):
        if stock_id not in self.__stock_list:
            return
        self.__canvas.paint('-' * self.__display_feat_len, name = stock_id)
        stock_data = self.__stock_list[stock_id][_LIST_DATA_OFF]
        history_len = len(stock_data[_LAST_TIME])
        for history in range(history_len):
            his_info = '{0:5s}:   {1:6.2f}  {2:>6.2f} {3:10d}'.format(stock_data[_LAST_TIME][history], \
                                                                      stock_data[_LAST_PRICE][history], \
                                                                      stock_data[_LAST_ADR][history], \
                                                                      stock_data[_LAST_TRANS][history])
            self.__canvas.paint(his_info, name = stock_id)
        self.__canvas.paint('-' * self.__display_feat_len, name = stock_id)

        detail_url = ''.join(['https://hq.finance.ifeng.com/q.php?l=', stock_id, ',&f=json;&r=0.9134400947969383&_=1507612356174'])
        response = self.__proxy_pool.get_page(detail_url)
        if len(response) == 0:
            self.__canvas.paint('failed to get detail of stock', name = stock_id)
            return
        detail = response.split(',')
        buy_list = detail[11:21]
        sell_list = detail[21:31]
        last_close = stock_data[_LAST_CLOSE]
        for stage in range(5):
            price = float(sell_list[4 - stage])
            transaction = int(float(sell_list[9 - stage]) / 100)
            color = canvas.GREEN if price < last_close else canvas.RED if price > last_close else canvas.WHITE
            if price:
                self.__canvas.paint('{0:6.2f}: {1:8d}'.format(price, transaction), front = color, name = stock_id)
            else:
                self.__canvas.paint('{0:>6s}: {1:8d}'.format('--.--', transaction), name = stock_id)
        self.__canvas.paint('-' * 16, name = stock_id)
        for stage in range(5):
            price = float(buy_list[stage])
            transaction = int(float(buy_list[5 + stage]) / 100)
            color = canvas.GREEN if price < last_close else canvas.RED if price > last_close else canvas.WHITE
            if price:
                self.__canvas.paint('{0:6.2f}: {1:8d}'.format(price, transaction), front = color, name = stock_id)
            else:
                self.__canvas.paint('{0:>6s}: {1:8d}'.format('--.--', transaction), name = stock_id)

    # create a new stock to monitor
    def __new_stock(self, stock_id):
        stock = dict()
        stock[_URL_KEY] = self.__url + stock_id + self.__type
        if stock_id in self.__stock_map_list.values():
            stock_name = list(self.__stock_map_list.keys())[list(self.__stock_map_list.values()).index(stock_id)]
            if len(stock_name) < _STOCK_NAME_LEN:
                blank = ' ' * (_STOCK_NAME_LEN - len(stock_name))
                stock_name = '{}{}{}'.format(blank, stock_name, blank)
        else:
            stock_name = ' ' * _STOCK_NAME_LEN * common.MAND_LENGTH
        stock[_NAME_KEY] = stock_name
        stock[_LAST_CLOSE] = 0.0
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
                    price = float(re.sub('"', '', response[1:-1]).split(',')[2])
                    if price != 0:
                        virtual_property += price * stock_item[1][_STOCK_NUM_KEY]
                    else:
                        virtual_property += stock_item[1][_STOCK_PRICE_KEY] * stock_item[1][_STOCK_NUM_KEY]
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
                break
            last_action_date = tools.get_date(-1, last_action_date)
        return last_virtual_property

    # display property
    def __property_display(self):
        self.__canvas.paint('-' * self.__display_feat_len, name = _PROPERTY)
        current_property = self.__property_lib.get_data(datalib.form_lkey([datalib.DATA_KEY, self.__today, _PROPERTY_KEY]))
        if self.__end_date == '':
            last_property = current_property
        else:
            last_property = self.__property_lib.get_data(datalib.form_lkey([datalib.DATA_KEY, self.__end_date, _PROPERTY_KEY]))
        last_virtual_property = self.__get_last_virtual_property()
        self.__canvas.paint('property: {0:9.2f}  profit_today: {1:8.2f} ratio: {2:-6.2f}%'.format(current_property, current_property - last_property, \
                                                                                                  (current_property - last_property) / last_property * 100), name = _PROPERTY)
        if last_virtual_property:
            self.__canvas.paint(' virtual: {0:9.2f} action_profit: {1:8.2f} ratio: {2:-6.2f}%'.format(last_virtual_property, current_property - last_virtual_property, \
                                                                                                      (current_property - last_virtual_property) / last_property * 100), name = _PROPERTY)
        self.__canvas.paint('    cash: {:9.2f}'.format(self.__property_lib.get_data(datalib.form_lkey([datalib.DATA_KEY, self.__today, _CASH_KEY]))), name = _PROPERTY)
        stock_data = self.__get_property_stock()
        for stock in stock_data.items():
            if _STOCK_PRICE_KEY in stock[1]:
                self.__canvas.paint('   stock: {0} price: {1:-6.2f} number: {2:-6} value: {3:-10.2f} pcost: {4:-5.2f} ratio: {5:-6.2f}%'.format(
                                    stock[1][_STOCK_ID_KEY], stock[1][_STOCK_PRICE_KEY],
                                    stock[1][_STOCK_NUM_KEY], stock[1][_STOCK_PRICE_KEY] * stock[1][_STOCK_NUM_KEY],
                                    stock[1][_STOCK_PCOST_KEY],
                                    (stock[1][_STOCK_PRICE_KEY] / stock[1][_STOCK_PCOST_KEY] - 1) * 100), name = _PROPERTY)

    def __stop_alarm(self):
        for c_alarm in self.__alarm:
            c_alarm.stop()
        self.__alarm.clear()

    def __display_cursor_refresh(self, pre, cur):
        self.__canvas.delete_format([_STOCK_HEAD_BUF + pre, 0, 0], other = canvas.HIGHLIGHT)
        self.__canvas.insert_format([_STOCK_HEAD_BUF + cur, 0, 0], other = canvas.HIGHLIGHT)

    # display each stock price
    def __display_price(self):
        self.__canvas.paint('{} {}'.format('-' * self.__display_feat_len, _VIEW_MODEL if self.__view_model else _COMMAND_MODEL))
        stocks_price_list = []
        self.__canvas.paint(tools.get_time_str(tools.TIME_HOUR, tools.TIME_SECOND, ':'))
        property_status = self.__property_lib.get_data()[self.__today]
        total_property = property_status[_CASH_KEY]
        market_suspended = False
        stock_lib = property_status[_STOCK_KEY] if _STOCK_KEY in property_status else dict()
        for n, stock_item in enumerate(sorted(self.__stock_list.items(), key = lambda d:d[1][_LIST_ID_OFF])):
            stock_id = stock_item[0]
            stock_data = stock_item[1][_LIST_DATA_OFF]
            stock_name = stock_data[_NAME_KEY]
            response = self.__proxy_pool.get_page(stock_data[_URL_KEY])
            # update property with last price if suspended
            if len(response) == 0:
                market_suspended = True
                if stock_id in stock_lib:
                    total_property += stock_lib[stock_id][_STOCK_PRICE_KEY] * stock_lib[stock_id][_STOCK_NUM_KEY]
                continue
            price = re.sub('"', '', response[1:-1]).split(',')
            ctime = re.sub(':\d\d$', '', price[0].split()[1])
            cprice = float(price[2])
            crate = float(price[3])
            ctransaction = int(price[6])
            if len(stock_data[_LAST_TIME]) == 0 or stock_data[_LAST_TIME][-1] != ctime:
                transaction = int(price[6])
                self.__stock_history_append(stock_data[_LAST_TIME], ctime)
                self.__stock_history_append(stock_data[_LAST_PRICE], cprice)
                self.__stock_history_append(stock_data[_LAST_ADR], crate)
                self.__stock_history_append(stock_data[_LAST_TRANS], ctransaction)
            else:
                transaction = int(price[6]) - stock_data[_LAST_TRANS][-1]
                stock_data[_LAST_PRICE][-1] = cprice
                stock_data[_LAST_ADR][-1] = crate
                stock_data[_LAST_TRANS][-1] = ctransaction

            stock_price = '{sid:2d} | {stock_id} {stock_name} {price:7.2f} {rate:7.2f} {trans:7d}'.format(sid = n + 1,
                                                                                                          stock_id = stock_id,
                                                                                                          stock_name = stock_name,
                                                                                                          price = cprice,
                                                                                                          rate = crate,
                                                                                                          trans = transaction)
            if self.__select_lib.lhas_key(datalib.form_lkey([datalib.DATA_KEY, stock_id])):
                stock_price = '{} {}'.format(stock_price, _SELECT_SIGN)
            if n == self.__stock_list_cursor:
                self.__canvas.paint(stock_price, other = canvas.HIGHLIGHT)
            else:
                self.__canvas.paint(stock_price)
            stock_data[_LAST_CLOSE] = float('{:.2f}'.format(cprice / (100 + crate) * 100))
            # update price and property
            if stock_id in stock_lib:
                price_lkey = datalib.form_lkey([datalib.DATA_KEY, self.__today, _STOCK_KEY, stock_id, _STOCK_PRICE_KEY])
                if cprice != 0:
                    total_property += cprice * stock_lib[stock_id][_STOCK_NUM_KEY]
                    self.__property_lib.set_data(price_lkey, cprice)
                else:
                    total_property += self.__property_lib.get_data(price_lkey) * stock_lib[stock_id][_STOCK_NUM_KEY]
        if market_suspended:
            self.__canvas.paint('stock market suspended')
            return
        self.__property_lib.set_data(datalib.form_lkey([datalib.DATA_KEY, self.__today, _PROPERTY_KEY]), total_property)

    # display all stock markets
    def __display_market(self):
        self.__canvas.clear_area()
        if self.__display_feat[_PROPERTY_INDEX]:
            self.__property_display()
        self.__display_price()
        for stock_id in self.__display_feat[_DETAIL_INDEX]:
            self.__show_detail(stock_id)
        self.__canvas.display()  # DEBUG

    # write data lib
    def __write_data_lib(self):
        self.__property_lib.write_data_lib()
        self.__select_lib.write_data_lib()
        self.__proxy_pool.write_data_lib()
