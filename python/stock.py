#!/usr/bin/env python
# coding=utf-8
'''Module for stock data scrap

Magtroid @ 2017-08-11 01:30
method for stock'''

# import library
from bs4 import BeautifulSoup
import canvas
import common
import copy
import datalib
import mio
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

ADR_KEY = 'adr'
TAPE_ADR_KEY = 'tadr'

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
    '''
    public:
      insert_stock_data
      insert_stock_detail_data
      update_stock_data
      get_stock_lib
      lib_file
      get_stock_data  # main function
      write_stock_data
    private:
      __parse_date
      __parse_period_data
      __get_stock_detail_data
      __write_data_lib

    resource has two types:
      1) string: stock id
      2) dict:   stock lib
    '''
    def __init__(self, resource, proxy_pool = None):
        self.__disable_controler = True  # TODO
        self.__stock_data_url = 'http://api.finance.ifeng.com'
        self.__stock_detail_data_url = 'http://vip.stock.finance.sina.com.cn/quotes_service/view/vMS_tradehistory.php?'
        if proxy_pool == None:
            self.__proxy_pool = proxypool.ProxyPool()
        else:
            self.__proxy_pool = proxy_pool
        self.__proxy_pool.set_threshold(15000)
        self.__status = _VALID
        if isinstance(resource, str):  # stock id
            self.__stock_code = parse_stock_code(resource)
            if not self.__stock_code:
                self.__status = _INVALID
            self.__data_lib_file = STOCK_DIR + self.__stock_code + '.lib'
            self.__stock_lib = datalib.DataLib(self.__data_lib_file, self.__disable_controler)
            self.__stock_lib.load_data_lib(schedule = False)
            self.__data_lib_detail_file = STOCK_DIR + self.__stock_code + '_detail.lib'
            self.__stock_detail_lib = datalib.DataLib(self.__data_lib_detail_file, self.__disable_controler)
            self.__stock_detail_lib.load_data_lib(schedule = False)
        elif isinstance(resource, dict):  # stock lib
            self.__stock_lib = datalib.DataLib(resource, self.__disable_controler)
            self.__data_lib_file = self.__stock_lib.lib_file()
            self.__stock_code = self.__data_lib_file.split('/')[-1].split('.')[0]  # xx/xx/id.lib
            self.__data_lib_detail_file = STOCK_DIR + self.__stock_code + '_detail.lib'
            self.__stock_detail_lib = datalib.DataLib(self.__data_lib_detail_file, self.__disable_controler)
            self.__stock_detail_lib.load_data_lib(schedule = False)
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

    # insert stock detail data
    def insert_stock_detail_data(self, stock_detail_data):
        self.__stock_detail_lib.insert_data(common.EMPTY_KEY, stock_detail_data, _DATE_KEY)

    # update stock data
    def update_stock_data(self, lkey, stock_data):
        for item in stock_data.items():
            lkey_feature = datalib.form_lkey([datalib.DATA_KEY, lkey, stock_data[_DATE_KEY], item[0]])
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
    def get_stock_data(self, need_detail = False):
        for period in self.__stock_period_set:
            if self.__status == _INVALID:
                break
            period_key = list(period.keys())[0]
            period_value = list(period.values())[0]
            period_url = '{root_url}/{period}/?{code}={stock_code}&type={period_type}'.format(
                          root_url = self.__stock_data_url,
                          period = period_value[0],
                          code = period_value[1],
                          stock_code = self.__stock_code,
                          period_type = period_value[2])
            log.VLOG(period_url)
            self.__parse_period_data(period_url, period_key)
        if need_detail:
            detail_finished = False
            while not detail_finished:
                log.VLOG('insert target detail date (xxxx.xx.xx)')
                log.VLOG('\tor insert "n/N" to cancel')
                target_date = mio.stdin()
                if re.match('^\d{4}\.\d{2}\.\d{2}$', target_date):
                    self.__get_stock_detail_data(target_date)
                elif target_date in common.CMD_QUIT:
                    break
                else:
                    log.VLOG('not support this type')
                    continue
        log.VLOG('done stock {stock_code}'.format(stock_code = self.__stock_code))
        return True if self.__status == _VALID else False

    # write stock data
    def write_stock_data(self):
        if self.__status == _VALID:
            self.__write_data_lib()

    # parse stock date
    def __parse_date(self, date_str):
        date = ''
        segs = str(date_str).split()
        if not tools.date_valid(list(map(int, segs[0].split('-')))):
            return date
        date += '.'.join(segs[0].split('-'))
        if len(segs) is 2:
            date += '.' + '.'.join(segs[1].split(':'))
        return date

    # parse data form a period url
    def __parse_period_data(self, url, period):
        page = self.__proxy_pool.get_page(url, self.__get_page_type, regex = '^{"record')
        if not page:
            log.VLOG('failed to get period page: {page}'.format(page = url))
            return
        stock_data = page[page.find('['):-1][2:-2].split('],[')
        # check if stock exist
        if not stock_data or len(stock_data) is 1 and not stock_data[0]:
            self.__status = _INVALID
            log.VLOG('invalid stock')
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
            period_data_unit[_HIGH_KEY] = float(data_segs[2])
            period_data_unit[_CLOSE_KEY] = float(data_segs[3])
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

    # get each deal in target date
    def __get_stock_detail_data(self, target_date):
        lkey = datalib.form_lkey([datalib.DATA_KEY, target_date])
        if self.__stock_detail_lib.lhas_key(lkey):
            log.VLOG('detail date exist: {date}'.format(date = target_date))
            return
        url_date = re.sub('\.', '-', target_date)
        detail_page_url = '{detail_url}symbol={stock_code}&date={date}'.format(
                           detail_url = self.__stock_detail_data_url,
                           stock_code = self.__stock_code,
                           date = url_date)
        detail_data_unit = dict()
        detail_data_unit[_DATE_KEY] = target_date
        detail_data_unit[_DETAIL_KEY] = []
        detail_minute_unit = []
        ctime = '00.00'
        for ipage in range(1, 200):
            detail_url = '{base_url}&page={page}'.format(base_url = detail_page_url, page = ipage)
            page = self.__proxy_pool.get_page(detail_url)
            if not page:
                log.VLOG('failed to get period page: {page}'.format(page = detail_url))
                continue
            soup = BeautifulSoup(page, common.HTML_PARSER)
            detail_segment = soup.select('table.datatbl tbody tr')
            print(detail_url)
            if len(detail_segment) <= 1:
                log.VLOG('finish detail scrap in date: {date}, all page: {page}'.format(date = target_date, page = ipage))
                break
            for itr in range(len(detail_segment) - 1):
                td = detail_segment[itr].select('td')
                th = detail_segment[itr].select('th')
                time = th[0].get_text().split(':')
                hm = '{hour}.{minute}'.format(hour = time[0], minute = time[1])
                sec = int(time[2])
                if hm != ctime:
                    if ctime != '00.00':
                        detail_data_unit[_DETAIL_KEY].append(copy.deepcopy(detail_minute_unit))
                    detail_minute_unit.clear()
                    detail_minute_unit.append(hm)
                    detail_minute_unit.append([])
                    ctime = hm
                buy_sell = '+' if th[1].get_text() == '买盘' else '-' if th[1].get_text() == '卖盘' else '='
                detail_deal_unit = [sec, buy_sell, float(td[0].get_text()), int(td[3].get_text())]
                detail_minute_unit[_DETAIL_TRADE_OFF].append(detail_deal_unit)
            tools.sleep(1)
        self.insert_stock_detail_data(detail_data_unit)

    # write stock data lib
    # config is for lib history TODO
    def __write_data_lib(self, config = None):
        self.__stock_lib.write_data_lib(backup = False)
        self.__stock_detail_lib.write_data_lib(backup = False)
        self.__proxy_pool.write_data_lib()

# training data dir
_TRAINING_DIR = './datalib/crf/'

# invest state
_EMPTY_STATE = 'empty'
_FULLY_STATE = 'fully'

_SERVICE_CHARGE = -0.7

# training file
_DEFAULT_FILE = 'crf_train_'

# k_line_model
_INDEX_MODEL = '__index__'
_KLINES_MODEL = '__klines__'
# k_line_list
_DATE_OFF = 0
_OPEN_OFF = 1
_CLOSE_OFF = 2
_HIGH_OFF = 3
_LOW_OFF = 4
_ADR_OFF = 5
_KLINE_DETAIL_STRUCT = [[0, 7, 20]]
_KLINE_REDUNT = 0.05
_KLINE_MIN_INDENSE = 40
_KLINE_MAX_INDENSE = 120
_KLINE_INDENSE_STEP = 20
_KLINE_SPARSE = 2
_KLINE_DETAIL = 'kline_detail'

# detail feature
_DETAIL_KEY = 'detail'
_DAILY_DETAIL = 'daily_detail'
_DETAIL_MINUTE_OFF = 0
_DETAIL_TRADE_OFF = 1
_DDATA_SEC_OFF = 0
_DDATA_BS_OFF = 1  # buy sell
_DDATA_PRICE_OFF = 2
_DDATA_TRANS_OFF = 3
_MIN_PRICE_OFF = 0
_MIN_TRANS_OFF = 1

_DAILY_AXIS_PRICE_WIDTH = 10
_DAILY_AXIS_ADR_WIDTH = 10
_DAILY_AXIS_PRICE_RATIO = 0.6

# data process class
class StockData(object):
    '''
    public
      display_data  # main function
      get_stock_data_with_tape
      select_stock
      stock_lib_data
      get_ad_ratio
      k_line
      display_daily_line
    private
      __get_weekday_strategy
      __form_kline_list
      __get_last_close
      __get_kline_range
      __get_daily_range
      __update_skip_off
      __draw_kline
      __display_kline
      __kline_detail
      __add_min_dict
      __daily_line
      __draw_daily_line
      __apply_strategy
      __gen_crf_data
      __oppotrend
      __fetch_stock_data
      __write_crf_data
    '''
    def __init__(self, resource):
        self.__status = _VALID
        self.__disable_controler = True
        if isinstance(resource, str):  # stock id
            self.__stock_code = parse_stock_code(resource)
            if not self.__stock_code:
                self.__status = _INVALID 
            self.__data_lib_file = STOCK_DIR + self.__stock_code + '.lib'
            self.__stock_lib = datalib.DataLib(self.__data_lib_file, self.__disable_controler)
            self.__stock_lib.load_data_lib(schedule = False)
            self.__data_lib_detail_file = STOCK_DIR + self.__stock_code + '_detail.lib'
            self.__stock_detail_lib = datalib.DataLib(self.__data_lib_detail_file, self.__disable_controler)
            self.__stock_detail_lib.load_data_lib(schedule = False)
        else:
            self.__status = _INVALID
        self.__canvas = canvas.CANVAS()

    # return stock lib data
    def stock_lib_data(self):
        return self.__stock_lib.get_data()

    # data process with strategy or generate training data
    def display_data(self, begin, end, data_key = _DAY_KEY):
        # self.__apply_strategy(_DAY_KEY)
        return self.__gen_crf_data(begin, end, data_key = data_key)
        # self.__oppotrend(_DAY_KEY)

    def get_stock_data_with_tape(self, begin, end, data_key = _DAY_KEY):
        stock_data = []
        tape_stock_id = 'sh000001'
        data_stock = self.__stock_lib.get_data()[data_key]
        tape_stock = StockData(tape_stock_id)
        data_tape = tape_stock.stock_lib_data()[data_key]
        date = begin
        while not tools.date_compare(date, end) == tools.EQUAL:
            date_str = tools.date_list_to_str(date)
            if date_str in data_stock and date_str in data_tape:
                cstock_data = dict()
                stock_data_unit = data_stock[date_str]
                tape_data_unit = data_tape[date_str]
                stock_ratio = stock_data_unit[_ADVANCE_DECLINE_RATIO_KEY]
                tape_ratio = tape_data_unit[_ADVANCE_DECLINE_RATIO_KEY]
                cstock_data[_DATE_KEY] = date_str
                cstock_data[ADR_KEY] = stock_ratio
                cstock_data[TAPE_ADR_KEY] = tape_ratio
                stock_data.append(cstock_data)
            date = tools.get_date(1, date)
        return stock_data

    def select_stock(self, begin, end, data_key = _DAY_KEY):
        select_stock_data = []
        data_stock = self.__stock_lib.get_data()[data_key]
        date = begin
        while not tools.date_compare(date, end) == tools.EQUAL:
            date_str = tools.date_list_to_str(date)
            stock_data_unit = data_stock[date_str]
            
            date = tools.get_date(1, date)
        return select_stock_data

    # calculate ad ratio from a target date
    def get_ad_ratio(self, date):
        ratio = 100.0
        cdate = list(map(int, date.split('.')))
        today = tools.get_date()
        data = self.__stock_lib.get_data()[_DAY_KEY]
        while not tools.date_compare(cdate, today) == tools.EQUAL:
            date_str = tools.date_list_to_str(cdate)
            if date_str in data:
                ratio *= (100 + data[date_str][_ADVANCE_DECLINE_RATIO_KEY]) / 100
            cdate = tools.get_date(1, cdate)
        return ratio

    # draw k lines of target stock
    def k_line(self):
        datas = self.__stock_lib.get_data()
        model = _INDEX_MODEL
        while True:
            if model == _INDEX_MODEL:
                command = mio.choose_command(list(datas.keys()))
                if command == 'q':
                    break
                else:
                    offs = 0
                    cursor = 0
                    max_kline = _KLINE_MIN_INDENSE
                    cdata = datas[command]
                    model = _KLINES_MODEL
                    kline_list = self.__form_kline_list(cdata)
                    self.__canvas.new_area(_KLINE_DETAIL_STRUCT, name = _KLINE_DETAIL)
            else:  # model == _KLINES_MODEL:
                self.__display_kline(kline_list, [offs, cursor, max_kline])
                command = mio.choose_command(block = False, print_log = False)
                if command == mio.LEFT_KEY:
                    if cursor < len(kline_list) - 1:
                        cursor += 1
                elif command == mio.RIGHT_KEY:
                    if cursor > 0:
                        cursor -= 1
                elif command == mio.ENTER_KEY:
                    date = kline_list[-1 - cursor][_DATE_OFF]
                    daily_data = self.__stock_detail_lib.get_data()
                    if date in daily_data:
                        last_close = self.__get_last_close(date)
                        if not last_close:
                            continue
                        self.__canvas.new_area([], name = _DAILY_DETAIL)
                        self.__daily_line(daily_data[date], last_close, name = _DAILY_DETAIL)
                        while True:
                            command_daily = mio.choose_command(block = False, print_log = False)
                            if command_daily in common.CMD_QUIT:
                                self.__canvas.del_area(_DAILY_DETAIL)
                                break
                elif command == '-':
                    if max_kline < _KLINE_MAX_INDENSE:
                        max_kline += _KLINE_INDENSE_STEP
                elif command == '+':
                    if max_kline > _KLINE_MIN_INDENSE:
                        max_kline -= _KLINE_INDENSE_STEP
                elif command in ['q', 'esc']:
                    model = _INDEX_MODEL
                else:
                    pass
                offs = self.__update_skip_off(cursor, offs, max_kline, len(kline_list))

    # display daily detail lines
    def display_daily_line(self):
        datas = self.__stock_detail_lib.get_data()
        while True:
            command = mio.choose_command(list(datas.keys()))
            if command in common.CMD_QUIT:
                break
            else:
                cdata = datas[command]
                last_close = self.__get_last_close(command)
                if not last_close:
                    log.VLOG('this date has no day data: {}'.format(command))
                    continue
                self.__daily_line(cdata, last_close)

    # get weekday strategy, weekday in weekday out
    def __get_weekday_strategy(self):
        finished = False
        while not finished:
            log.VLOG('insert in and out weekday \d \d (0~6)')
            log.VLOG('\tor insert "n/q" to cancel')
            weekday = mio.stdin()
            if re.match('^[0-6] [0-6]$', weekday):
                [weekday_in, weekday_out] = list(map(int, re.search('^(\d \d)$', weekday).group(1).split()))
            elif weekday in common.CMD_QUIT:
                weekday_in = -1
                weekday_out = -1
            else:
                log.VLOG('not support this type')
                continue
            finished = True
        if weekday_in is not -1 and weekday_out is not -1:
            log.VLOG('strategy weekday in: {weekday_in}, out: {weekday_out}'.format(
                     weekday_in = weekday_in,
                     weekday_out = weekday_out))
        return [weekday_in, weekday_out]

    # form kline list contain date, open close high low pair
    def __form_kline_list(self, datas):
        kline_list = []
        cdate = tools.get_time_str(tools.TIME_YEAR, tools.TIME_DAY, '.')
        while len(kline_list) < len(datas):
            if cdate in datas:
                cdata = datas[cdate]
                ikline = [cdate, cdata[_OPEN_KEY], cdata[_CLOSE_KEY], cdata[_HIGH_KEY], cdata[_LOW_KEY], cdata[_ADVANCE_DECLINE_RATIO_KEY]]
                kline_list.append(ikline)
            cdate = tools.get_date(-1, cdate)
        kline_list.reverse()
        return kline_list

    def __get_last_close(self, c_date):
        datas = self.__stock_lib.get_data()[_DAY_KEY]
        if c_date in datas:
            c_data = datas[c_date]
            c_price = c_data[_CLOSE_KEY]
            c_rate = c_data[_ADVANCE_DECLINE_RATIO_KEY]
            last_close = float('{:.2f}'.format(c_price / (100 + c_rate) * 100))
        else:
            last_close = 0
        return last_close

    def __get_kline_range(self, kline_list, begin, end):
        top = 0
        bottom = 99999.99
        step = 0
        for idata in kline_list[begin : end]:
            top = max(idata[_HIGH_OFF], top)
            bottom = min(idata[_LOW_OFF], bottom)
        amp = top - bottom
        top += amp * _KLINE_REDUNT
        bottom -= amp * _KLINE_REDUNT
        return top, bottom

    def __get_daily_range(self, min_datas):
        price_t = 0
        price_b = 99999.99
        trans_t = 0
        for min_data in min_datas.values():
            if min_data:
                price_t = max(min_data[_MIN_PRICE_OFF], price_t)
                price_b = min(min_data[_MIN_PRICE_OFF], price_b)
                trans_t = max(min_data[_MIN_TRANS_OFF], trans_t)
        return price_t, price_b, trans_t

    def __update_skip_off(self, cursor, skip_off, width, data_num):
        head_len = 3
        while cursor > skip_off + width - head_len:
            if cursor > data_num - head_len:
                break
            skip_off += 1
        while cursor < skip_off + head_len - 1:
            if cursor < head_len - 1:
                break
            skip_off -= 1
        return skip_off

    def __draw_kline(self, data, n, highlight = False):
        x = _KLINE_SPARSE * n
        if data[_OPEN_OFF] != data[_CLOSE_OFF]:
            color = canvas.GREEN if data[_OPEN_OFF] < data[_CLOSE_OFF] else canvas.RED
        else:
            color = canvas.GREEN if data[_ADR_OFF] < 0 else canvas.RED
        line_up, line_down = [_OPEN_OFF, _CLOSE_OFF] if data[_OPEN_OFF] < data[_CLOSE_OFF] else [_CLOSE_OFF, _OPEN_OFF]
        for i in range(data[_HIGH_OFF], data[line_up]):
            self.__canvas.paint('│', coordinate = [i, x], front = color)
            if highlight:
                self.__canvas.insert_format([i, x, 1], other = canvas.HIGHLIGHT)
        if data[line_up] == data[line_down]:
            self.__canvas.insert_format([data[line_up] - 1, x, 1], other = canvas.UNDERLINE)
            self.__canvas.insert_format([data[line_up] - 1, x, 1], front = color)
            if highlight:
                self.__canvas.insert_format([data[line_up] - 1, x, 1], other = canvas.HIGHLIGHT)
        else:
            for i in range(data[line_up], data[line_down]):
                if color != '':
                    self.__canvas.insert_format([i, x, 1], back = color)
                else:
                    self.__canvas.insert_format([i, x, 1], other = canvas.INVERSE)
                if highlight:
                    self.__canvas.insert_format([i, x, 1], other = canvas.HIGHLIGHT)
        for i in range(data[line_down], data[_LOW_OFF]):
            self.__canvas.paint('│', coordinate = [i, x], front = color)
            if highlight:
                self.__canvas.insert_format([i, x, 1], other = canvas.HIGHLIGHT)

    # param is [offset, cursor, max_data_number] which means move to left offset and intensive of kline
    def __display_kline(self, kline_list, param):
        offset, cursor, max_kline_num = param
        cstruct = self.__canvas.get_area_struct()[1]
        height, width = len(cstruct), cstruct[0][1]
        data_num = min(len(kline_list), width, max_kline_num)
        begin = max(len(kline_list) - data_num - offset, 0)
        end = begin + data_num
        top, bottom = self.__get_kline_range(kline_list, begin, end)
        step = (top - bottom) / height
        display_list = [[x[_DATE_OFF]] + [int((top - y) / step) for y in x[_OPEN_OFF:_ADR_OFF]] + [x[_ADR_OFF]] for x in kline_list[begin : end]]
        icursor = data_num - cursor + offset - 1
        coord = [0, 0] if icursor > data_num / 2 else [0, int(width / 2)]
        self.__canvas.move_area(_KLINE_DETAIL, coord, module = canvas.MOVE_MODULE_TO)
        self.__canvas.erase()
        self.__canvas.clear_area()
        for n, ikline in enumerate(display_list):
            if n == icursor:
                self.__draw_kline(ikline, n, True)
            else:
                self.__draw_kline(ikline, n)
        self.__kline_detail(kline_list[-(cursor + 1)])
        self.__canvas.display()

    def __kline_detail(self, data):
        self.__canvas.paint('_' * 20, name = _KLINE_DETAIL)
        self.__canvas.paint('DATE : {}:'.format(data[_DATE_OFF]), name = _KLINE_DETAIL)
        self.__canvas.paint('OPEN : {:6.2f}'.format(data[_OPEN_OFF]), name = _KLINE_DETAIL)
        self.__canvas.paint('CLOSE: {:6.2f}'.format(data[_CLOSE_OFF]), name = _KLINE_DETAIL)
        self.__canvas.paint('HIGH : {:6.2f}'.format(data[_HIGH_OFF]), name = _KLINE_DETAIL)
        self.__canvas.paint('LOW  : {:6.2f}'.format(data[_LOW_OFF]), name = _KLINE_DETAIL)
        self.__canvas.paint('ADR  : {:6.2f}%'.format(data[_ADR_OFF]), name = _KLINE_DETAIL)

    # init 240 trade minute list
    def __add_min_dict(self, min_dict, hour, minute_range = None):
        # set minute range
        if minute_range is None:
            start = 0
            end = 59
        else:
            start = max(0, minute_range[0])
            end = min(59, minute_range[1])
        h_str = '0{}'.format(hour) if hour < 10 else '{}'.format(hour)
        for m in range(start, end + 1):
            m_str = '0{}'.format(m) if m < 10 else '{}'.format(m)
            hm = '{hour}.{minute}'.format(hour = h_str, minute = m_str)
            if hm not in min_dict:
                min_dict[hm] = []

    # draw daily detail line in name canvas, if no name, using found canvas
    def __daily_line(self, datas, last_close, name = None):
        min_dict = dict()
        self.__add_min_dict(min_dict, 9, [30, 59])
        self.__add_min_dict(min_dict, 10, [00, 59])
        self.__add_min_dict(min_dict, 11, [00, 30])
        self.__add_min_dict(min_dict, 13, [00, 59])
        self.__add_min_dict(min_dict, 14, [00, 59])
        self.__add_min_dict(min_dict, 15, [00, 00])

        for data_min in datas[_DETAIL_KEY]:
            hm = data_min[_DETAIL_MINUTE_OFF]
            mdata = data_min[_DETAIL_TRADE_OFF]
            mtrans = 0
            for trade_data in mdata:
                mtrans += trade_data[_DDATA_TRANS_OFF]
            mprice = mdata[-1][_DDATA_PRICE_OFF]
            min_dict[hm] = [mprice, mtrans]
        self.__draw_daily_line(min_dict, last_close, name = name)

    def __draw_daily_line(self, min_datas, last_close, name = None):
        cstruct = self.__canvas.get_area_struct(name = name)[1]
        height, width = len(cstruct), cstruct[0][1]
        data_width = width - _DAILY_AXIS_PRICE_WIDTH - _DAILY_AXIS_ADR_WIDTH
        self.__canvas.erase()
        self.__canvas.clear_area()
        x_step = int(data_width / len(min_datas))
        if x_step == 0:
            self.__canvas.paint('canvas too small for daily line, try larger canvas', name = name)
            self.__canvas.display()
            return

        price_height = int(height * _DAILY_AXIS_PRICE_RATIO)
        trans_height = height - price_height

        price_t, price_b, trans_t= self.__get_daily_range(min_datas)
        price_t = max(price_t, last_close)
        price_b = min(price_b, last_close)

        price_step = (price_t - price_b) / (price_height - 1)
        trans_step = trans_t / (trans_height - 1)
        last_price = last_close
        last_color = canvas.WHITE
        for y in range(price_height):
            y_price = float('{:.2f}'.format(price_t - price_step * y))
            axis_color = canvas.GREEN if y_price < last_close else canvas.RED if y_price > last_close else canvas.WHITE 
            self.__canvas.paint('{:6.2f}'.format(y_price), coordinate = [y, 0], front = axis_color, name = name)
            self.__canvas.paint('{:6.2f}%'.format((y_price - last_close) / last_close * 100),
                    coordinate = [y, _DAILY_AXIS_PRICE_WIDTH + x_step * len(min_datas)], front = axis_color, name = name)
        self.__canvas.insert_format([price_height - 1, 0, _DAILY_AXIS_PRICE_WIDTH + x_step * len(min_datas) + _DAILY_AXIS_ADR_WIDTH], other = canvas.UNDERLINE, name = name)
        for y in range(trans_height):
            self.__canvas.paint('{:.0f}'.format(trans_t - trans_step * y), coordinate = [y + price_height, 0], name = name)

        x = _DAILY_AXIS_PRICE_WIDTH
        for min_item in sorted(min_datas.items(), key = lambda d:d[0]):
            min_data = min_item[1]
            if not min_data:
                continue
            color = canvas.GREEN if min_data[_MIN_PRICE_OFF] < last_price else canvas.RED if min_data[_MIN_PRICE_OFF] > last_price else last_color
            price_y = int((price_t - min_data[_MIN_PRICE_OFF]) / price_step)
            self.__canvas.paint('•', coordinate = [price_y, x], name = name)
            trans_y = price_height + int((trans_t - min_data[_MIN_TRANS_OFF]) / trans_step)
            for y in range(trans_y, height):
                self.__canvas.paint('│', coordinate = [y, x], front = color, name = name)
            last_price = min_data[_MIN_PRICE_OFF]
            last_color = color
            x += x_step
        self.__canvas.display()

    # use strategy for specific day in and out
    def __apply_strategy(self, data_key):
        data = self.__stock_lib.get_data()[data_key]
        principal = 100.0
        service_charge = 0.0
        state = _EMPTY_STATE
        (start, end) = tools.get_date_duration()
        (weekday_in, weekday_out) = self.__get_weekday_strategy()
        if len(start) is 0 or len(end) is 0 or \
           weekday_in is -1 or weekday_out is -1:
            return
        date = start
        deal_num = 0
        while not tools.date_compare(date, end) == tools.EQUAL:
            date_str = tools.date_list_to_str(date)
            if date_str in data:
                log.VLOG(data[date_str], 1)
                data_unit = data[date_str]
                if data_unit[_WEEKDAY_KEY] == weekday_in and state == _EMPTY_STATE:
                    state = _FULLY_STATE
                if state == _FULLY_STATE:
                    log.VLOG('\t{date} profit: {profit:.2f}%'.format(date = date_str,
                                                                     profit = data_unit[_ADVANCE_DECLINE_RATIO_KEY]))
                    principal = principal * (100 + data_unit[_ADVANCE_DECLINE_RATIO_KEY]) / 100
                if data_unit[_WEEKDAY_KEY] == weekday_out and state == _FULLY_STATE:
                    deal_num += 1
                    # process service charge
                    service_charge -= principal * _SERVICE_CHARGE / 100
                    principal = principal * (100 + _SERVICE_CHARGE) / 100
                    log.VLOG('deal number{deal_num}, profit: {profit:.2f}%'.format(deal_num = deal_num,
                                                                                   profit = principal - 100))
                    state = _EMPTY_STATE
            date = tools.get_date(1, date)
        log.VLOG('total profit is {profit:.2f}%'.format(profit = principal - 100))
        log.VLOG('total service charge is {service:.2f}%'.format(service = service_charge))

    # generate training data for crf model
    def __gen_crf_data(self, begin, end, data_key = _DAY_KEY):
        crf_least_data_num = 30
        data = self.__stock_lib.get_data()[data_key]
        date = begin
        train_list = []
        while not tools.date_compare(date, end) == tools.EQUAL:
            date_str = tools.date_list_to_str(date)
            if date_str in data:
                train_vector = []
                log.VLOG(data[date_str], 1)
                data_unit = data[date_str]
                if _TURN_OVER_KEY not in data_unit:
                    f2 = 0.0
                elif data_unit[_TRANSACTION_KEY] == 0:
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
                # if len(train_list) > 0:
                #     train_list[-1].append(train_vector[0])  # next day
                # if len(train_list) > 2:
                #     train_list[-3].append(train_vector[0] + train_list[-1][0] + train_list[-2][0])  # next 3 day
                if len(train_list) > 4:
                    train_list[-5].append((100 + train_vector[0]) / 100 * (100 + train_list[-1][0]) / 100 * (100 + train_list[-2][0]) / 100 * (100 + train_list[-3][0]) / 100 * (100 + train_list[-4][0]))  # next 5 day
                train_list.append(train_vector)
            date = tools.get_date(1, date)
        if len(train_list) < crf_least_data_num:
            return []
        train_list.pop()
        train_list.pop()
        train_list.pop()
        train_list.pop()
        return train_list

    def __oppotrend(self, data_key):
        (start, end) = tools.get_date_duration()
        if len(start) == 0 or len(end) == 0:
            return
        stock_data = self.get_stock_data_with_tape(start, end, data_key = data_key)
        oppo_list = []
        oppo_unit = []
        for cstock_data in stock_data:
            stock_ratio = cstock_data[ADR_KEY]
            tape_ratio = cstock_data[TAPE_ADR_KEY]
            expect_ratio = tape_ratio * 3
            delta = stock_ratio - expect_ratio
            if expect_ratio > 0:
                weight = delta / expect_ratio
            else:
                weight = - delta / expect_ratio
            if weight > 1:
                judge = 'oppo_raise'
            elif weight < -1:
                judge = 'oppo_down'
            else:
                judge = ''

            if judge:
                if not oppo_unit:
                    oppo_unit.append(cstock_data[_DATE_KEY])
            if oppo_unit:
                oppo_unit.append('{}({})'.format(stock_ratio, tape_ratio))
            if not judge and oppo_unit:
                oppo_list.append(oppo_unit[:])
                oppo_unit.clear()
        for oppo_u in oppo_list:
            print(oppo_u)

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
            str_line = ('{str}\n').format(str = '\t'.join(list(map(str, vector))))
            fp.writelines(str_line)

if __name__ == '__main__':
    log.INFO('choose a stock id:')
    stock_id = tools.choose_file_from_dir(STOCK_DIR, print_log = False)
    log.INFO()
    if stock_id:
        stock_data = StockData(re.sub('\.lib$', '', stock_id))
        stock_data.k_line()
        # stock_data.display_daily_line()
    log.INFO('done')
