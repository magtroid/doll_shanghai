#!/usr/bin/env python
# coding=utf-8
'''Module for stock data scrap

Magtroid @ 2017-08-11 01:30
method for stock'''

# import library
from bs4 import BeautifulSoup
import common
import datalib
import proxypool
import re
import tools
import log

# const define
STOCK_DIR = './datalib/stocks/'
_SH_STOCK_CODE = 'sh'
_SZ_STOCK_CODE = 'sz'

# stock feature period
_DAY_KEY       = 'day'
_WEEK_KEY      = 'week'
_MONTH_KEY     = 'month'
_YEAR_KEY      = 'year'
_MINUTE_5_KEY  = 'minute5'
_MINUTE_15_KEY = 'minute15'
_MINUTE_30_KEY = 'minute30'
_MINUTE_60_KEY = 'minute60'

# stock feature
_DATE_KEY = 'date'
_OPEN_KEY = 'open'
_CLOSE_KEY = 'close'
_HIGH_KEY = 'high'
_LOW_KEY = 'low'
_WEEKDAY_KEY = 'weekday'
_TRANSACTION_KEY = 'transaction'
_ADVANCE_DECLINE_KEY = 'ad'
_ADVANCE_DECLINE_RATIO_KEY = 'adr'
_AVER_PRICE_5_KEY = 'pma5'
_AVER_PRICE_10_KEY = 'pma10'
_AVER_PRICE_20_KEY = 'pma20'
_AVER_TRANS_5_KEY = 'tma5'
_AVER_TRANS_10_KEY = 'tma10'
_AVER_TRANS_20_KEY = 'tma20'
_TURN_OVER_KEY = 'turnover'

_UNIT_STOCK_LEN = 15

# data period
_PERIOD_MINUTE    = None
_PERIOD_DAY_5     = None
_PERIOD_YEAR      = None
_PERIOD_DAY       = {_DAY_KEY : ('akdaily',   'code', 'last')}
_PERIOD_WEEK      = {_WEEK_KEY : ('akweekly',  'code', 'last')}
_PERIOD_MONTH     = {_MONTH_KEY : ('akmonthly', 'code', 'last')}
_PERIOD_MINUTE_5  = {_MINUTE_5_KEY : ('akmin', 'scode', '5')}
_PERIOD_MINUTE_15 = {_MINUTE_15_KEY : ('akmin', 'scode', '15')}
_PERIOD_MINUTE_30 = {_MINUTE_30_KEY : ('akmin', 'scode', '30')}
_PERIOD_MINUTE_60 = {_MINUTE_60_KEY : ('akmin', 'scode', '60')}

# stock status
_VALID = 'valid'      # valid if stock code exist
_INVALID = 'invalid'  # invalid if not exist

# common functions
# parse stock code into valid stock code 000001 -> sz000001
def parse_stock_code(code):
    if len(code) == 8 and re.match('(sh|sz)\d{6}', code):
        pass
    elif len(code) == 6 and re.match('\d{6}', code):
        if code[0] == '0':
            code = _SZ_STOCK_CODE + code
        elif code[0] == '6':
            code = _SH_STOCK_CODE + code
        elif code[0] == '3':
            code = _SZ_STOCK_CODE + code
        else:
            code = ''
    else:
        code = ''
    return code

# main class
class Stock(object):
    # public:
    #   insert_stock_data
    #   update_stock_data
    #   get_stock_lib
    #   lib_file
    #   get_stock_data  # main function
    #   write_stock_data
    # private:
    #   __parse_date
    #   __parse_period_data
    #   __write_data_lib

    # resource has two types:
    #   1) string: stock id
    #   2) dict:   stock lib
    def __init__(self, resource, vlog = 0, proxy_pool = None):
        self.__disable_controler = True  # TODO
        self.__vlog = log.VLOG(vlog)
        self.__stock_data_url = 'http://api.finance.ifeng.com'
        if proxy_pool == None:
            self.__proxy_pool = proxypool.ProxyPool(vlog = vlog)
        else:
            self.__proxy_pool = proxy_pool
        self.__status = _VALID
        if isinstance(resource, str):  # stock id
            self.__stock_code = parse_stock_code(resource)
            if not self.__stock_code:
                self.__status = _INVALID
            self.__data_lib_file = STOCK_DIR + self.__stock_code + '.lib'
            self.__stock_lib = datalib.DataLib(self.__data_lib_file, self.__disable_controler, vlog = 0)
            self.__stock_lib.load_data_lib()
        elif isinstance(resource, dict):  # stock lib
            self.__stock_lib = datalib.DataLib(resource, self.__disable_controler, vlog = 0)
            self.__data_lib_file = self.__stock_lib.lib_file()
            self.__stock_code = self.__data_lib_file.split('/')[-1].split('.')[0]  # xx/xx/id.lib
        else:
            self.__status = _INVALID
        self.__get_page_type = common.URL_WRITE
        self.__stock_period_set = (_PERIOD_DAY, _PERIOD_WEEK, \
                                   _PERIOD_MONTH, \
                                   _PERIOD_MINUTE_5, _PERIOD_MINUTE_15, \
                                   _PERIOD_MINUTE_30, _PERIOD_MINUTE_60)

    # insert stock data
    def insert_stock_data(self, lkey, stock_data):
        self.__stock_lib.insert_data(lkey, stock_data, _DATE_KEY)

    # update stock data
    def update_stock_data(self, lkey, stock_data):
        for item in stock_data.items():
            lkey_feature = datalib.form_lkey([datalib.DATA_KEY, lkey, datalib.DATA_FEATURE, item[0]])
            if self.__stock_lib.lhas_key(lkey_feature):
                self.__stock_lib.set_data(lkey_feature, item[1])

    # get stock lib
    def get_stock_lib(self):
        return self.__stock_lib.get_data_lib()

    # get lib file
    def lib_file(self):
        return self.__data_lib_file

    # get stock data
    # return true or false if success or not
    def get_stock_data(self):
        for period in self.__stock_period_set:
            if self.__status == _INVALID:
                break
            period_key = period.keys()[0]
            period_value = period.values()[0]
            period_url = '{root_url}/{period}/?{code}={stock_code}&type={period_type}'.format( \
                          root_url = self.__stock_data_url, \
                          period = period_value[0], \
                          code = period_value[1], \
                          stock_code = self.__stock_code, \
                          period_type = period_value[2])
            self.__vlog.VLOG(period_url)
            self.__parse_period_data(period_url, period_key)
        self.__vlog.VLOG('done stock {stock_code}'.format(stock_code = self.__stock_code))
        return True if self.__status == _VALID else False

    # write stock data
    def write_stock_data(self):
        if self.__status == _VALID:
            self.__write_data_lib()

    # parse stock date
    def __parse_date(self, date_str):
        date = ''
        segs = str(date_str).split()
        if not tools.date_valid(map(int, segs[0].split('-'))):
            return date
        date += '.'.join(segs[0].split('-'))
        if len(segs) is 2:
            date += '.' + '.'.join(segs[1].split(':'))
        return date

    # parse data form a period url
    def __parse_period_data(self, url, period):
        page = self.__proxy_pool.get_page(url, self.__get_page_type, regex = '^{"record')
        if not page:
            self.__vlog.VLOG('failed to get period page: {page}'.format(page = url))
            return
        stock_data = page[page.find('['):-1][2:-2].split('],[')
        # check if stock exist
        if not stock_data or len(stock_data) is 1 and not stock_data[0]:
            self.__status = _INVALID
            self.__vlog.VLOG('invalid stock')
            return
        for data in stock_data:
            if period == _DAY_KEY or period == _WEEK_KEY or period == _MONTH_KEY:
                data_segs = data[1:-1].split('","')
                data_segs = [x.replace(',', '') for x in data_segs]
            else:
                data_segs = data[1:].split(',')
                data_segs = [x.replace('"', '') for x in data_segs]
            period_data_unit = dict()
            data_date = self.__parse_date(data_segs[0])
            if not data_date:
                continue
            period_data_unit[_DATE_KEY] = data_date

            period_data_unit[_WEEKDAY_KEY] = tools.get_weekday(data_date)
            period_data_unit[_OPEN_KEY] = float(data_segs[1])
            period_data_unit[_CLOSE_KEY] = float(data_segs[2])
            period_data_unit[_HIGH_KEY] = float(data_segs[3])
            period_data_unit[_LOW_KEY] = float(data_segs[4])
            period_data_unit[_TRANSACTION_KEY] = float(data_segs[5])
            period_data_unit[_ADVANCE_DECLINE_KEY] = float(data_segs[6])
            period_data_unit[_ADVANCE_DECLINE_RATIO_KEY] = float(data_segs[7])
            period_data_unit[_AVER_PRICE_5_KEY] = float(data_segs[8])
            period_data_unit[_AVER_PRICE_10_KEY] = float(data_segs[9])
            period_data_unit[_AVER_PRICE_20_KEY] = float(data_segs[10])
            period_data_unit[_AVER_TRANS_5_KEY] = float(data_segs[11])
            period_data_unit[_AVER_TRANS_10_KEY] = float(data_segs[12])
            period_data_unit[_AVER_TRANS_20_KEY] = float(data_segs[13])
            if len(data_segs) is _UNIT_STOCK_LEN:
                period_data_unit[_TURN_OVER_KEY] = float(data_segs[14]) if data_segs[14] else 0
            lkey = datalib.form_lkey([datalib.DATA_KEY, period, data_date])
            if self.__stock_lib.lhas_key(lkey):
                self.update_stock_data(period, period_data_unit)
            else:
                self.insert_stock_data(period, period_data_unit)

    # write stock data lib
    # config is for lib history TODO
    def __write_data_lib(self, config = None):
        self.__stock_lib.write_data_lib(backup = False)
        self.__proxy_pool.write_data_lib()

# const define
_CMD_QUIT = 'qQnN'

# training data dir
_TRAINING_DIR = './datalib/crf/'

# invest state
_EMPTY_STATE = 'empty'
_FULLY_STATE = 'fully'

_SERVICE_CHARGE = -0.7

# training file
_DEFAULT_FILE = 'crf_train_'

# data process class
class StockData(object):
    # public
    #   display_data  # main function
    #   get_ad_ratio
    # private
    #   __get_date_duration
    #   __get_weekday_strategy
    #   __apply_strategy
    #   __gen_crf_data
    #   __fetch_stock_data
    #   __write_crf_data
    def __init__(self, resource, fp = None, vlog = 0):
        self.__vlog = log.VLOG(vlog)
        self.__status = _VALID
        self.__disable_controler = True
        if isinstance(resource, str):  # stock id
            self.__stock_code = parse_stock_code(resource)
            if not self.__stock_code:
                self.__status = _INVALID 
            self.__data_lib_file = STOCK_DIR + self.__stock_code + '.lib'
            self.__stock_lib = datalib.DataLib(self.__data_lib_file, self.__disable_controler, vlog = 0)
            self.__stock_lib.load_data_lib()
            if fp == None:
                self.__fp = _TRAINING_DIR + _DEFAULT_FILE + self.__stock_code + '.train'
            else:
                self.__fp = fp
        else:
            self.__status = _INVALID

    # data process with strategy or generate training data
    def display_data(self):
        data = self.__stock_lib.get_data()
        # self.__apply_strategy(data[_DAY_KEY])
        self.__gen_crf_data(data[_DAY_KEY])

    # calculate ad ratio from a target date
    def get_ad_ratio(self, date):
        ratio = 100.0
        cdate = map(int, date.split('.'))
        today = tools.get_date()
        data = self.__stock_lib.get_data()[_DAY_KEY]
        while not tools.date_compare(cdate, today) == tools.EQUAL:
            date_str = tools.date_list_to_str(cdate)
            if date_str in data:
                ratio *= (100 + data[date_str][_ADVANCE_DECLINE_RATIO_KEY]) / 100
            cdate = tools.get_date(1, cdate)
        return ratio

    # get strategy duration
    def __get_date_duration(self):
        finished = False
        while not finished:
            self.__vlog.VLOG('print a date duration (xxxx.xx.xx~yyyy.yy.yy/\d year/\d month/\d week)')
            self.__vlog.VLOG('\tor insert "n/q" to cancel')
            date_range = tools.stdin()
            if re.match('^\d+ year$', date_range):
                day = common.YEAR_DAY * int(re.search('(\d+)', date_range).group(1))
                start = tools.get_date(-day)
                end = tools.get_date()
            elif re.match('^\d+ month$', date_range):
                day = common.MONTH_DAY * int(re.search('(\d+)', date_range).group(1))
                start = tools.get_date(-day)
                end = tools.get_date()
            elif re.match('^\d+ week$', date_range):
                day = common.WEEK_DAY * int(re.search('(\d+)', date_range).group(1))
                start = tools.get_date(-day)
                end = tools.get_date()
            elif re.match('^\d{4}\.\d{2}\.\d{2}~\d{4}\.\d{2}\.\d{2}$', date_range):
                start = map(int, date_range.split('~')[0].split('.'))
                end = map(int, date_range.split('~')[1].split('.'))
                if not tools.date_valid(start) or \
                   not tools.date_valid(end) or \
                   not tools.date_compare(start, end) == tools.LESS:
                    self.__vlog.VLOG('insert date invalid')
                    continue
            elif date_range in _CMD_QUIT:
                start = []
                end = []
            else:
                self.__vlog.VLOG('not support this type')
                continue
            finished = True
        if len(start) is not 0 and len(end) is not 0:
            self.__vlog.VLOG('strategy date range:{start} to {end}'.format( \
                              start = ' '.join(map(str, start)), \
                              end = ' '.join(map(str, end))))
        return [start, end]

    # get weekday strategy, weekday in weekday out
    def __get_weekday_strategy(self):
        finished = False
        while not finished:
            self.__vlog.VLOG('insert in and out weekday \d \d (0~6)')
            self.__vlog.VLOG('\tor insert "n/q" to cancel')
            weekday = tools.stdin()
            if re.match('^[0-6] [0-6]$', weekday):
                [weekday_in, weekday_out] = map(int, re.search('^(\d \d)$', weekday).group(1).split())
            elif weekday in _CMD_QUIT:
                weekday_in = -1
                weekday_out = -1
            else:
                self.__vlog.VLOG('not support this type')
                continue
            finished = True
        if weekday_in is not -1 and weekday_out is not -1:
            self.__vlog.VLOG('strategy weekday in: {weekday_in}, out: {weekday_out}'.format( \
                              weekday_in = weekday_in, \
                              weekday_out = weekday_out))
        return [weekday_in, weekday_out]

    # use strategy for specific day in and out
    def __apply_strategy(self, data):
        principal = 100.0
        service_charge = 0.0
        state = _EMPTY_STATE
        (start, end) = self.__get_date_duration()
        (weekday_in, weekday_out) = self.__get_weekday_strategy()
        if len(start) is 0 or len(end) is 0 or \
           weekday_in is -1 or weekday_out is -1:
            return
        date = start
        deal_num = 0
        while not tools.date_compare(date, end) == tools.EQUAL:
            date_str = tools.date_list_to_str(date)
            if date_str in data:
                self.__vlog.VLOG(data[date_str], 1)
                data_unit = data[date_str]
                if data_unit[_WEEKDAY_KEY] == weekday_in and state == _EMPTY_STATE:
                    state = _FULLY_STATE
                if state == _FULLY_STATE:
                    self.__vlog.VLOG('\t{date} profit: {profit:.2f}%'.format(date = date_str, \
                                                                         profit = data_unit[_ADVANCE_DECLINE_RATIO_KEY]))
                    principal = principal * (100 + data_unit[_ADVANCE_DECLINE_RATIO_KEY]) / 100
                if data_unit[_WEEKDAY_KEY] == weekday_out and state == _FULLY_STATE:
                    deal_num += 1
                    # process service charge
                    service_charge -= principal * _SERVICE_CHARGE / 100
                    principal = principal * (100 + _SERVICE_CHARGE) / 100
                    self.__vlog.VLOG('deal number{deal_num}, profit: {profit:.2f}%'.format(deal_num = deal_num, \
                                                                                       profit = principal - 100))
                    state = _EMPTY_STATE
            date = tools.get_date(1, date)
        self.__vlog.VLOG('total profit is {profit:.2f}%'.format(profit = principal - 100))
        self.__vlog.VLOG('total service charge is {service:.2f}%'.format(service = service_charge))

    # generate training data for crf model
    def __gen_crf_data(self, data):
        (start, end) = self.__get_date_duration()
        if len(start) is 0 or len(end) is 0:
            return
        date = start
        train_list = []
        while not tools.date_compare(date, end) == tools.EQUAL:
            date_str = tools.date_list_to_str(date)
            if date_str in data:
                train_vector = []
                self.__vlog.VLOG(data[date_str], 1)
                data_unit = data[date_str]
                if _TURN_OVER_KEY not in data_unit:
                    f2 = 0.0
                elif data_unit[_TURN_OVER_KEY] == 0:
                    continue
                else:
                    f2 = data_unit[_TURN_OVER_KEY]
                f1 = data_unit[_ADVANCE_DECLINE_RATIO_KEY]
                f3 = (data_unit[_HIGH_KEY] - data_unit[_LOW_KEY]) * 100 / \
                      (data_unit[_CLOSE_KEY] * 100 / (100 + f1))
                f4 = (data_unit[_CLOSE_KEY] - data_unit[_AVER_PRICE_5_KEY]) * 100 / \
                      data_unit[_AVER_PRICE_5_KEY]
                f5 = (data_unit[_CLOSE_KEY] - data_unit[_AVER_PRICE_10_KEY]) * 100 / \
                      data_unit[_AVER_PRICE_10_KEY]
                f6 = (data_unit[_CLOSE_KEY] - data_unit[_AVER_PRICE_20_KEY]) * 100 / \
                      data_unit[_AVER_PRICE_20_KEY]
                f7 = (data_unit[_TRANSACTION_KEY] - data_unit[_AVER_TRANS_5_KEY]) * 100 / \
                      data_unit[_AVER_TRANS_5_KEY]
                f8 = (data_unit[_TRANSACTION_KEY] - data_unit[_AVER_TRANS_10_KEY]) * 100 / \
                      data_unit[_AVER_TRANS_10_KEY]
                f9 = (data_unit[_TRANSACTION_KEY] - data_unit[_AVER_TRANS_20_KEY]) * 100 / \
                      data_unit[_AVER_TRANS_20_KEY]
                train_vector.append(f1)  # ad ratio
                train_vector.append(f2)  # turn over
                train_vector.append(f3)  # amplitude
                train_vector.append(f4)  # aver 5 price ad ratio
                train_vector.append(f5)  # aver 10 price ad ratio
                train_vector.append(f6)  # aver 20 price ad ratio
                train_vector.append(f7)  # aver 5 trans ad ratio
                train_vector.append(f8)  # aver 10 trans ad ratio
                train_vector.append(f9)  # aver 20 trans ad ratio
                if len(train_list) > 0:
                    train_list[-1].append(train_vector[0])  # next day
                if len(train_list) > 2:
                    train_list[-3].append(train_vector[0] + train_list[-1][0] + train_list[-2][0])  # next 3 day
                if len(train_list) > 4:
                    train_list[-5].append(train_vector[0] + train_list[-1][0] + train_list[-2][0] + train_list[-3][0] + train_list[-4][0])  # next 5 day

                train_list.append(train_vector)
            date = tools.get_date(1, date)
        # train_list = train_list[20:]
        train_list_final = []
        for train_vector in train_list:
            train_list_final.append([self.__fetch_stock_data(x) for x in train_vector])
        if isinstance(self.__fp, str):
            with tools.open_file(self.__fp) as fp:
                self.__write_crf_data(train_list_final, fp)
        else:
            self.__write_crf_data(train_list_final, self.__fp)

    # fetch stock data into int
    def __fetch_stock_data(self, data):
        data = int(float(data) * 100)
        if data < -10000:
            data_fetch = 0
        elif data < -5000:
            data_fetch = 1
        elif data < -2000:
            data_fetch = 2
        elif data < -1000:
            data_fetch = 3
        elif data < -500:
            data_fetch = 4
        elif data < -200:
            data_fetch = 5
        elif data < 0:
            data_fetch = 6
        elif data < 200:
            data_fetch = 7
        elif data < 500:
            data_fetch = 8
        elif data < 1000:
            data_fetch = 9
        elif data < 2000:
            data_fetch = 10
        elif data < 5000:
            data_fetch = 11
        elif data < 10000:
            data_fetch = 12
        else:
            data_fetch = 13
        return data_fetch

    # write crf data
    def __write_crf_data(self, train_list, fp):
        for vector in train_list:
            str_line = ('{str}\n').format(str = '\t'.join(map(str, vector)))
            fp.writelines(str_line)
