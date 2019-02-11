#!/usr/bin/env python
# coding=utf-8
'''
Module for lianjia data scrap

Magtroid @ 2017-06-21 20:23
methods for lianjia
'''

# import library
from bs4 import BeautifulSoup
import common
import datalib
import mio
import proxypool
import re
import sys
import tools
import log

# const define
# data unit dict
_ID_KEY        = datalib.DATA_FEATURE
_DATE_KEY      = 'date'
_REGION_KEY    = 'region'
_SUBREGION_KEY = 'subregion'
_UNIT_KEY      = 'unit'
_HANG_KEY      = 'hang'
_DEAL_KEY      = 'deal'

_NO_STOP = 99

_CMD_DAY    = '1 day'
_CMD_WEEK   = '1 week'
_CMD_MONTH  = '1 month'
_CMD_ALL    = 'all'
_CMD_UPDATE = 'update'

_ONE_DAY       = 1
_ONE_WEEK      = 7
_ONE_MONTH     = 30
_VERY_BEGINING = 3000

# self.__region dict
_REGION_NAME_KEY = 'name'
_REGION_SUBREGION_KEY = 'subregion'
_REGION_NUM_KEY = 'num'

# region_index dict
_INDEX_REGION_KEY = 'region'
_INDEX_SUBREGION_KEY = 'subregion'

# data lib const
_DATA_BUFFER = 1000
_PAGE_DATA_NUM = 30

# go on switch
_STOP_THRESHOLD = 2
_STOP_SUBREGION = 1
_STOP_ALL = 0

# lib history
_HISTORY_KEY = 'history'
_HISTORY_TIME = 'time'
_HISTORY_DATA_START = 'start_time'
_HISTORY_DATA_END = 'end_time'
_HISTORY_STATUS = 'status'
_HISTORY_UPDATE_NUM = 'update'
_HISTORY_FINISH = 'finished'
_HISTORY_INTERRUPT = 'interrupt'

# filter domain
_DOMAIN_FILTER = ['燕郊', '香河']

# date special word
_DATE_SPECIAL_WORD = '近30天内成交'

# page try time
_PAGE_WAIT_TIME = [5, 5, 10, 10, 30, 30, 60, 60, 120, 120, 360, 360]

# main class
class LianJia(object):
    # public:
    #   aplay_data
    #   insert_lianjia_data
    #   insert_lianjia_config
    #   get_lianjia_data  # main function
    # private:
    #   __calc_data_duration
    #   __get_data_duration
    #   __in_search_range
    #   __get_scrap_duration
    #   __fix_start_date
    #   __get_region
    #   __get_subregion
    #   __get_page_num
    #   __get_subregion_data
    #   __choose_scrap_region
    #   __check_write_data
    #   __get_data
    #   __parse_data
    #   __form_lib_history
    #   __write_data_lib

    def __init__(self, city, proxy_pool = None):
        self.__city = city
        self.__city_url = 'https://' + self.__city + '.lianjia.com'
        self.__mask_duration = 31
        self.__start_date = []  # scrap start date
        self.__end_date = []  # scrap end date
        self.__region = dict()
        self.__subregion_number = 0
        if proxy_pool == None:
            self.__proxy_pool = proxypool.ProxyPool()
        else:
            self.__proxy_pool = proxy_pool
        self.__proxy_pool.set_threshold(150)
        self.__data_lib_file = './datalib/' + self.__city + '_lianjia.lib'
        self.__disable_controler = False
        self.__lianjia_lib = datalib.DataLib(self.__data_lib_file, self.__disable_controler)
        self.__lianjia_lib.load_data_lib()
        self.__get_data_duration()
        self.__new_data_num = 0
        self.__new_data_tail = 0  # for check if data enough to write
        self.__latest_month_deal = 0  # latest deal for one month
        self.__stop_threshold = _STOP_THRESHOLD
        self.__go_on = self.__stop_threshold  # 0 for stop, 1 for stop region, more for go on
        self.__get_page_type = common.URL_WRITE

    # aplay data TODO
    def aplay_data(self, data):
        for i in range(len(data)):
            log.VLOG('{}\t{}\t{}'.format(data[i][0], data[i][1], data[i][2]))

    # insert lianjia data
    def insert_lianjia_data(self, lkey, lianjia_data):
        if self.__lianjia_lib.insert_data(lkey, lianjia_data, _ID_KEY):
            self.__new_data_num += 1

    # insert lianjia config
    def insert_lianjia_config(self, lkey, lianjia_config):
        self.__lianjia_lib.insert_config(lkey, lianjia_config, _HISTORY_TIME)

    # get lianjia data
    def get_lianjia_data(self):
        if not self.__get_scrap_duration():
            return

        self.__get_region()
        target_region, target_subregion = self.__choose_scrap_region()

        region_index = dict()
        region_count = 0
        prev_data_num = 0
        for sregion in self.__region.items():
            if target_region != _CMD_ALL and target_region != sregion[1][_REGION_NAME_KEY]:
                continue
            region_count += 1
            region_index[_INDEX_REGION_KEY] = sregion[1][_REGION_NAME_KEY]
            subregion_count = 0
            for ssubregion in sregion[1][_REGION_SUBREGION_KEY].items():
                if target_subregion != _CMD_ALL and target_subregion != ssubregion[1]:
                    continue
                subregion_count += 1
                subregion_url = ssubregion[0]
                subregion_name = ssubregion[1]
                region_index[_INDEX_SUBREGION_KEY] = subregion_name
                log.VLOG('scrap region: %s %d/%d(%d/%d)' % (subregion_url, region_count, len(self.__region), \
                                                            subregion_count, len(sregion[1][_REGION_SUBREGION_KEY])))
                self.__get_subregion_data(subregion_url, region_index)

                log.VLOG('all data number: {}'.format(self.__lianjia_lib.data_num()))
                log.VLOG('new data number: {}'.format(self.__new_data_num))

                # check go on
                if self.__go_on is _STOP_ALL:
                    break
            sregion[1][_REGION_NUM_KEY] = self.__new_data_num - prev_data_num
            prev_data_num = self.__new_data_num
            if self.__go_on is _STOP_ALL:
                break

        log.VLOG('{} ~ {} update {} deals'.format(self.__start_date, self.__end_date, self.__new_data_num))
        for sregion in sorted(self.__region.items(), key=lambda d:d[1][_REGION_NUM_KEY], reverse=True):
            log.VLOG('{} update {} deals'.format(sregion[1][_REGION_NAME_KEY], sregion[1][_REGION_NUM_KEY]))
        log.VLOG('deal number in latest one month: {}'.format(self.__latest_month_deal))

        log.VLOG('finished write data')
        write_config = _HISTORY_INTERRUPT if not self.__go_on else _HISTORY_FINISH
        self.__write_data_lib(write_config)
        log.VLOG('done lianjia')

    # calculate lianjia data lib date duration
    def __calc_data_duration(self):
        data_num = self.__lianjia_lib.data_num()
        log.VLOG('begin to calculate date range')
        count = 0
        data = self.__lianjia_lib.get_data()
        for item in data.items():
            count += 1
            tools.schedule(count, data_num)
            # filter non bj domains
            if item[1][_REGION_KEY] in _DOMAIN_FILTER:
                continue
            date = item[1][_DATE_KEY]
            if len(self.__start_date) is 0:
                self.__start_date = date
            if len(self.__end_date) is 0:
                self.__end_date = date
            date_compare_start = tools.date_compare(date, self.__start_date)
            date_compare_end = tools.date_compare(date, self.__end_date)
            if date_compare_start == tools.LESS or date_compare_start == tools.INCLUDE:
                self.__start_date = date
            if date_compare_end == tools.LARGER or date_compare_end == tools.INCLUDE:
                self.__end_date = date
        log.VLOG('success! date range: {} ~ {}'.format(self.__start_date, self.__end_date))

    # get data duration from data lib
    def __get_data_duration(self):
        history_lkey = datalib.CONFIG_KEY + _HISTORY_KEY
        if self.__lianjia_lib.lhas_key(history_lkey):
            histories = self.__lianjia_lib.get_data(history_lkey)
            for history in sorted(histories.items(), key=lambda d:int(d[0]), reverse=True):
                if history[1][_HISTORY_STATUS] == HISTORY_FINISH:
                    self.__start_date = history[1][_HISTORY_DATE_START]
                    self.__end_date = history[1][_HISTORY_DATE_END]
                    return
                else:
                    continue
        self.__calc_data_duration()

    # check if date in search range
    def __in_search_range(self, date):
        if not tools.date_compare(self.__start_date, date) == tools.LARGER and \
           not tools.date_compare(date, self.__end_date) == tools.LARGER:
            return True
        else:
            return False

    # type in scrap target duration, according to data duration range
    def __get_scrap_duration(self):
        finished = False
        while not finished:
            log.VLOG('insert date_range duration (1 day/1 week/1 month/xxxx.xx.xx~yyyy.yy.yy/update/all)')
            log.VLOG('\tor insert "n/N" to cancel')
            date_range = mio.stdin()
            if date_range == _CMD_ALL:
                self.__get_page_type = common.URL_READ
                self.__start_date = tools.get_date(-_VERY_BEGINING)
                self.__end_date = tools.get_date()
                self.__stop_threshold = _NO_STOP
            elif date_range == _CMD_DAY:
                self.__start_date = tools.get_date(-_ONE_DAY)
                self.__end_date = tools.get_date()
            elif date_range == _CMD_WEEK:
                self.__start_date = tools.get_date(-_ONE_WEEK)
                self.__end_date = tools.get_date()
            elif date_range == _CMD_MONTH:
                self.__start_date = tools.get_date(-_ONE_MONTH)
                self.__end_date = tools.get_date()
            elif date_range == _CMD_UPDATE:
                self.__get_page_type = common.URL_WRITE
                if len(self.__end_date) is 0:
                    self.__start_date = tools.get_date(-_VERY_BEGINING)
                else:
                    self.__start_date = self.__end_date
                self.__end_date = tools.get_date()
            elif date_range in common.CMD_QUIT:
                self.__start_date = []
                self.__end_date = []
            elif re.match('^\d{4}\.\d{2}\.\d{2}~\d{4}\.\d{2}\.\d{2}$', date_range):
                self.__get_page_type = common.URL_WRITE
                start_date = list(map(int, date_range.split('~')[0].split('.')))
                end_date = list(map(int, date_range.split('~')[1].split('.')))
                if tools.date_valid(start_date) and \
                   tools.date_valid(end_date) and \
                   tools.date_compare(start_date, end_date) == tools.LESS:
                    self.__start_date = start_date
                    self.__end_date = end_date
                else:
                    log.VLOG('insert date invalid')
                    continue
            else:
                log.VLOG('not support this type')
                continue
            finished = True
        if len(self.__start_date) is 0 or len(self.__end_date) is 0:
            return False
        else:
            self.__fix_start_date()
            log.VLOG('start to get data in time duration: {} to {}'.format(' '.join(list(map(str, self.__start_date))), ' '.join(list(map(str, self.__end_date)))))
            return True

    # fix start date to mask days before
    def __fix_start_date(self):
        mask_date = tools.get_date(-self.__mask_duration)
        if tools.date_compare(self.__start_date, mask_date) == tools.LARGER:
            self.__start_date = mask_date

    # get region and subregion of lianjia
    def __get_region(self):
        log.VLOG('begin to get region')
        cjurl = self.__city_url + '/chengjiao'
        page = self.__proxy_pool.get_page(cjurl, common.URL_READ)
        if not page:
            log.VLOG('failed to scrap region page')
            return
        else:
            soup = BeautifulSoup(page, common.HTML_PARSER)
            region_count = 0
            region_elements = soup.select('div[data-role="ershoufang"] div a')
            for region_element in region_elements:
                region_count += 1
                region_name = str(region_element.get_text())
                region_url = tools.parse_href_url(region_element[common.HREF_KEY], self.__city_url)
                log.VLOG('region {}/{} {}'.format(region_count, len(region_elements), region_name))
                self.__region[region_url] = dict()
                self.__region[region_url][_REGION_NAME_KEY] = region_name
                self.__region[region_url][_REGION_SUBREGION_KEY] = self.__get_subregion(region_url)
                self.__region[region_url][_REGION_NUM_KEY] = 0
        log.VLOG('all {} regions'.format(self.__subregion_number))

    # get subregion from a region
    # empty if no subregion of failed
    def __get_subregion(self, url):
        city_url = url[:url.find('chengjiao')]
        page = self.__proxy_pool.get_page(url, common.URL_READ)
        subregion = dict()
        if not page:
            log.VLOG('failed to scrap subregion')
            return subregion
        else:
            soup = BeautifulSoup(page, common.HTML_PARSER)
            subregion_classes = soup.select('div[data-role="ershoufang"] div')
            if len(subregion_classes) < 2:
                log.VLOG('no subregion for page {}'.format(url))
                return subregion
            subregion_count = 0
            subregion_elements = subregion_classes[1].select('a')
            for subregion_element in subregion_elements:
                self.__subregion_number += 1
                subregion_count += 1
                subregion_name = str(subregion_element.get_text())
                subregion_url = tools.parse_href_url(subregion_element[common.HREF_KEY], city_url)
                log.VLOG('\tsub region {}/{} {}'.format(subregion_count, len(subregion_elements), subregion_name))
                subregion[subregion_url] = subregion_name
        return subregion

    # get page number of a subregion
    def __get_page_num(self, url):
        page_num = 0
        page = self.__proxy_pool.get_page(url, common.URL_READ)
        if not page:
            log.VLOG('failed to scrap page number page')
        else:
            soup = BeautifulSoup(page, common.HTML_PARSER)
            for page_segment in soup.select('[comp-module="page"]'):
                page_num = int(re.search('totalPage":(\d+)', page_segment['page-data']).group(1))
        return page_num

    # get lianjia data of a subregion
    def __get_subregion_data(self, url, region_index):
        page_num = self.__get_page_num(url)  # get page number
        for page in range(page_num):
            log.VLOG('\tscrap page: {cur_page}/{total_page} {region}:{subregion}'.format(cur_page = page + 1,
                                                                                         total_page = page_num,
                                                                                         region = region_index[_INDEX_REGION_KEY],
                                                                                         subregion = region_index[_INDEX_SUBREGION_KEY]))
            data_url = tools.parse_href_url('/pg%d' % page, url)
            try_time = 0
            while not self.__get_data(data_url, region_index):
                if try_time < len(_PAGE_WAIT_TIME):
                    log.VLOG('failed to get page data, wait {} s and try again'.format(_PAGE_WAIT_TIME[try_time]))
                    tools.sleep(_PAGE_WAIT_TIME[try_time])
                    try_time += 1
                else:
                    if page == page_num - 1:
                        break
                    else:
                        self.__go_on = _STOP_ALL
                        return
            self.__check_write_data()
            if self.__go_on <= _STOP_SUBREGION:
                log.VLOG('subregion finished {} '.format(region_index[_INDEX_SUBREGION_KEY]))
                self.__go_on = self.__stop_threshold
                return

    # choose scrap region, subregion, return region, subregion
    def __choose_scrap_region(self):
        region = ''
        subregion = ''
        region_list = [x[_REGION_NAME_KEY] for x in self.__region.values()]
        region_list.append(_CMD_ALL)
        command = mio.choose_command(region_list)
        if command == 'cancel' or command == 'q':
            log.VLOG('region canceled...')
        else:
            region = command
            if region != _CMD_ALL:
                for iregion in self.__region.items():
                    if iregion[1][_REGION_NAME_KEY] == region:
                        subregion_list = list(iregion[1][_SUBREGION_KEY].values())
                        subregion_list.append(_CMD_ALL)
                        command = mio.choose_command(subregion_list)
                        if command == 'cancel' or command == 'q':
                            log.VLOG('subregion canceled...')
                        else:
                            subregion = command
            else:
                subregion = _CMD_ALL
        return region, subregion

    # check if data enough to write data, for safety
    def __check_write_data(self):
        data_tail = self.__new_data_num % _DATA_BUFFER
        if self.__new_data_tail >= _DATA_BUFFER - _PAGE_DATA_NUM and \
           data_tail <= _PAGE_DATA_NUM:
            log.VLOG('write data')
            self.__write_data_lib()
            self.__new_data_tail = data_tail

    # get lianjia data from url
    def __get_data(self, url, region_index):
        page = self.__proxy_pool.get_page(url, self.__get_page_type)
        print(url)
        if page == common.URL_EXIST:
            log.VLOG('page exists: {}'.format(url))
            return True
        elif page == '':
            log.VLOG('failed to get url page: {}'.format(url))
            return False
        else:  # success to get page
            return self.__parse_data(page, region_index)

    # parse data page to get lianjia data lib
    def __parse_data(self, page, region_index):
        soup = BeautifulSoup(page, common.HTML_PARSER)
        flag_all_date_out = True
        data_elements = soup.select('.listContent li')
        log.VLOG('page data number {}'.format(len(data_elements)))
        if len(data_elements) == 0:
            return False
        for data_element in data_elements:
            data_element_a = data_element.a
            data_element_div = data_element.div
            lianjia_unit = dict()
            lianjia_unit[_ID_KEY] = str(re.search('(\w*).html', data_element_a[common.HREF_KEY]).group(1))
            # filter mask
            if len(data_element_div.select('.dealDate')) == 0 or _DATE_SPECIAL_WORD == data_element_div.select('.dealDate')[0].get_text():
                log.VLOG('masked for 1 month limit')
                flag_all_date_out = False
                self.__latest_month_deal += 1
                continue
            lianjia_unit[_DATE_KEY] = list(map(int, data_element_div.select('.dealDate')[0].get_text().split('.')))

            # if in search range
            if not self.__in_search_range(lianjia_unit[_DATE_KEY]):
                log.VLOG('not in search range {data_date} ({begin_date} ~ {end_date})'.format(data_date = lianjia_unit[_DATE_KEY],
                                                                                              begin_date = self.__start_date,
                                                                                              end_date = self.__end_date))
                if flag_all_date_out and not tools.date_compare(lianjia_unit[_DATE_KEY], self.__start_date) == tools.LESS:
                    flag_all_date_out = False
                continue
            flag_all_date_out = False

            # if exists data
            if self.__lianjia_lib.lhas_key(datalib.form_lkey([datalib.DATA_KEY, lianjia_unit[_ID_KEY]])):
                log.VLOG('id exist: {}'.format(lianjia_unit[_ID_KEY]))
                continue

            lianjia_unit[_REGION_KEY] = region_index[_INDEX_REGION_KEY]
            lianjia_unit[_SUBREGION_KEY] = region_index[_INDEX_SUBREGION_KEY]

            unit_element = data_element_div.select('.unitPrice')
            hang_element = data_element_div.select('.dealCycleTxt span')
            deal_element = data_element_div.select('.totalPrice')
            # process str if price is not listed
            unit_str = re.sub('[^\d.]', '', unit_element[0].get_text()) if unit_element else '0'
            hang_str = re.sub('[^\d.]', '', hang_element[0].get_text()) if hang_element else '0'
            deal_str = re.sub('[^\d.]', '', deal_element[0].get_text()) if deal_element else '0'
            lianjia_unit[_UNIT_KEY] = float(unit_str) if unit_str else 0
            lianjia_unit[_HANG_KEY] = float(hang_str) if hang_str else 0
            lianjia_unit[_DEAL_KEY] = float(deal_str) if deal_str else 0
            self.insert_lianjia_data(common.EMPTY_KEY, lianjia_unit)

        if self.__stop_threshold != _NO_STOP:
            if flag_all_date_out:
                self.__go_on -= 1
            else:
                self.__go_on = self.__stop_threshold
        return True

    # form lib history to store last scrap time, data range, data number
    def __form_lib_history(self, config):
        lib_history = dict()
        self.__start_date = []
        self.__end_date = []
        self.__calc_data_duration()
        lib_history[_HISTORY_TIME] = tools.get_time_str(tools.TIME_YEAR, tools.TIME_SECOND, '')
        lib_history[_HISTORY_STATUS] = config
        lib_history[_HISTORY_UPDATE_NUM] = self.__new_data_num
        lib_history[_HISTORY_DATA_START] = self.__start_date
        lib_history[_HISTORY_DATA_END] = self.__end_date
        return lib_history

    # write lianjia data lib
    def __write_data_lib(self, config = None):
        if config:
            lib_history = self.__form_lib_history(config)
            self.insert_lianjia_config(_HISTORY_KEY, lib_history)
        self.__lianjia_lib.write_data_lib()
        self.__proxy_pool.write_data_lib()

# const define
_REGION_NUM_KEY  = 'num'
_REGION_DATA_KEY = 'data'
_REGION_ALL_KEY  = 'all'

_DISTR_NUM_KEY = 'num'
_DISTR_UNIT_NUM_KEY = 'unit_num'
_DISTR_HANG_NUM_KEY = 'hang_num'
_DISTR_DEAL_NUM_KEY = 'deal_num'

# data process class
class LianJiaData(object):
    # public
    #   display_data
    # private:
    #   __calc_data_duration
    #   __add_date_range
    #   __del_date_range
    #   __get_region
    #   __get_data_distribution
    #   __display_region_data
    #   __write_data_lib

    def __init__(self, city):
        self.__city = city
        self.__start_date = []
        self.__end_date = []
        self.__disable_controler = True
        self.__data_lib_file = './datalib/' + self.__city + '_lianjia.lib'
        self.__lianjia_lib = datalib.DataLib(self.__data_lib_file, self.__disable_controler)
        self.__lianjia_lib.load_data_lib()
        self.__calc_data_duration()
        self.__region = dict()
        self.__date_range = dict()
        self.__add_date_range(2014, [1, 12])
        self.__add_date_range(2015, [1, 12])
        self.__add_date_range(2016, [1, 12])
        self.__add_date_range(2017, [1, 12])
        self.__add_date_range(2018, [1, 12])
        self.__add_date_range(2019, [1, 6])

    # display data
    # command to choose region
    def display_data(self):
        self.__get_region()
        while 1:
            command = mio.choose_command(self.__region)
            if command == 'cancel' or command == 'q':
                log.VLOG('canceled...')
                break
            data_distribution = self.__get_data_distribution(command)
            self.__display_region_data(data_distribution)

    # calculate lianjia data lib date duration
    def __calc_data_duration(self):
        data_num = self.__lianjia_lib.data_num()
        log.VLOG('begin to calculate date range')
        count = 0
        data = self.__lianjia_lib.get_data()
        for item in data.items():
            count += 1
            tools.schedule(count, data_num)
            date = item[1][_DATE_KEY]
            if len(self.__start_date) is 0:
                self.__start_date = date
            if len(self.__end_date) is 0:
                self.__end_date = date
            # update data duration
            date_compare_start = tools.date_compare(date, self.__start_date)
            date_compare_end = tools.date_compare(date, self.__end_date)
            if date_compare_start == tools.LESS or date_compare_start == tools.INCLUDE:
                self.__start_date = date
            if date_compare_end == tools.LARGER or date_compare_end == tools.INCLUDE:
                self.__end_date = date
        log.VLOG('success! date range: {begin_date} ~ {end_date}'.format(begin_date = self.__start_date,
                                                                         end_date = self.__end_date))

    # add date range in data show
    # if no month, add all target year, each year is a 12 list
    def __add_date_range(self, year, month_range = None):
        # add new year key
        if year not in self.__date_range:
            self.__date_range[year] = [0] * 12
        # set month range
        if month_range is None:
            start = 1
            end = 12
        else:
            start = 1 if month_range[0] < 1 else month_range[0]
            end = 12 if month_range[1] > 12 else month_range[1]
        # set 1 for added month
        for month in range(start - 1, end):
            self.__date_range[year][month] = 1

    # delete date range in data show
    # if no month, delete all target year
    def __del_date_range(self, year, month_range = None):
        if year not in self.__date_range:
            log.VLOG('no this year')
            return
        if not month_range:
            start = 1
            end = 12
        else:
            start = 1 if month_range[0] < 1 else month_range[0]
            end = 12 if month_range[1] > 12 else month_range[1]
        # set 0 for deleted month
        for month in range(start - 1, end):
            self.__date_range[year][month] = 0
        # check if all month 0 of one year, delete this year
        all = 0
        for month in range(12):
            all += self.__date_range[year][month]
        if all is 0:
            del self.__date_range[year]

    # gen a region dict, include data number and each data
    def __get_region(self):
        count = 0
        data = self.__lianjia_lib.get_data()
        data_num = self.__lianjia_lib.data_num()
        for sdata in data.items():
            count += 1
            tools.schedule(count, data_num)
            region = sdata[1][_REGION_KEY]
            if region not in self.__region:
                self.__region[region] = dict()
                self.__region[region][_REGION_NUM_KEY] = 1
                self.__region[region][_REGION_DATA_KEY] = dict()
            else:
                self.__region[region][_REGION_NUM_KEY] += 1
            self.__region[region][_REGION_DATA_KEY][sdata[0]] = sdata[1]

        self.__region[_REGION_ALL_KEY] = dict()
        self.__region[_REGION_ALL_KEY][_REGION_NUM_KEY] = data_num
        self.__region[_REGION_ALL_KEY][_REGION_DATA_KEY] = data
        for sitem in sorted(self.__region.items(), key=lambda d:d[1][_REGION_NUM_KEY], reverse=True):
            sregion = sitem[0]
            per = int(self.__region[sregion][_REGION_NUM_KEY] / float(data_num) * 10000) / 100.0 if data_num else 0
            log.VLOG('{subregion}: {subregion_num} ({percent:5.2f}%)'.format(subregion = sregion,
                                                                             subregion_num = self.__region[sregion][_REGION_NUM_KEY],
                                                                             percent = per))

    # get choose region distribution
    def __get_data_distribution(self, region):
        data_distribution = dict()
        for year in self.__date_range.keys():
            for month in range(12):
                if self.__date_range[year][month]:
                    date = [year, month + 1]
                    data_distribution[str(date)] = dict()
                    data_distribution[str(date)][_DISTR_NUM_KEY] = 0
                    data_distribution[str(date)][_UNIT_KEY] = 0
                    data_distribution[str(date)][_DISTR_UNIT_NUM_KEY] = 0
                    data_distribution[str(date)][_HANG_KEY] = 0
                    data_distribution[str(date)][_DISTR_HANG_NUM_KEY] = 0
                    data_distribution[str(date)][_DEAL_KEY] = 0
                    data_distribution[str(date)][_DISTR_DEAL_NUM_KEY] = 0

        regions = region.split(':')
        if len(regions) == 2:
            region = regions[0]
            subregion = regions[1]
        else:
            region = regions[0]
            subregion = ''

        for item in self.__region[region][_REGION_DATA_KEY].items():
            if not subregion == '' and not subregion == item[1][_SUBREGION_KEY]:
                continue
            date = item[1][_DATE_KEY]
            price = item[1][_UNIT_KEY]
            hang = item[1][_HANG_KEY]
            deal = item[1][_DEAL_KEY]
            # normalize date to year month format and pass invalid date
            if len(date) is 3:
                date = date[:2]
            if len(date) is 1:
                continue
            if str(date) not in data_distribution:
                continue

            data_distribution[str(date)][_DISTR_NUM_KEY] += 1
            if price > 0:
                data_distribution[str(date)][_UNIT_KEY] += price
                data_distribution[str(date)][_DISTR_UNIT_NUM_KEY] += 1
            if hang > 0:
                data_distribution[str(date)][_HANG_KEY] += hang
                data_distribution[str(date)][_DISTR_HANG_NUM_KEY] += 1
            if deal > 0:
                data_distribution[str(date)][_DEAL_KEY] += deal
                data_distribution[str(date)][_DISTR_DEAL_NUM_KEY] += 1
        return data_distribution

    # display distribution region data
    def __display_region_data(self, region_distribution_data):
        for year in sorted(self.__date_range.keys()):
            for month in range(12):
                if self.__date_range[year][month]:
                    date = [year, month + 1]
                    per = 0
                    if region_distribution_data[str(date)][_DISTR_UNIT_NUM_KEY]:
                        region_distribution_data[str(date)][_UNIT_KEY] /= region_distribution_data[str(date)][_DISTR_UNIT_NUM_KEY]
                    if region_distribution_data[str(date)][_DISTR_HANG_NUM_KEY]:
                        region_distribution_data[str(date)][_HANG_KEY] /= region_distribution_data[str(date)][_DISTR_HANG_NUM_KEY]
                    if region_distribution_data[str(date)][_DISTR_DEAL_NUM_KEY]:
                        region_distribution_data[str(date)][_DEAL_KEY] /= region_distribution_data[str(date)][_DISTR_DEAL_NUM_KEY]
                    if region_distribution_data[str(date)][_HANG_KEY]:
                        per = region_distribution_data[str(date)][_DEAL_KEY] / region_distribution_data[str(date)][_HANG_KEY] * 100
                    log.VLOG('{date}\t{deal_num:10d}\t{unit:13.2f}\t{hang:13.2f}\t{deal:13.2f}\t{percent:5.2f}%'.format(
                        date = str(date),
                        deal_num = region_distribution_data[str(date)][_DISTR_NUM_KEY],
                        unit = region_distribution_data[str(date)][_UNIT_KEY],
                        hang = region_distribution_data[str(date)][_HANG_KEY],
                        deal = region_distribution_data[str(date)][_DEAL_KEY],
                        percent = per))

    # write data lib
    def __write_data_lib(self, config = None):
        if config:
            lib_history = self.__form_lib_history(config)
            self.insert_lianjia_config(_HISTORY_KEY, lib_history)
        self.__lianjia_lib.write_data_lib()
        self.__proxy_pool.write_data_lib()
