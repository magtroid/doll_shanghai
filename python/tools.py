#!/usr/bin/env python
# coding=utf-8
'''tools for common tools

Magtroid @ 2017-06-26 15:58
'''

# import library
from datetime import datetime, timedelta
import common
import log
import mmath
import mio
import os
import proxypool
import psutil
import random
import re
import sys
import time

# const define
_TERMINAL_BUFFER = 10

_SCHEDULE_LEN = 50

_SOLAR_MONTH= [4, 6, 9, 11]
_LUNAR_MONTH = [1, 3, 5, 7, 8, 10, 12]

INCLUDED = -2
LESS     = -1
EQUAL    =  0
LARGER   =  1
INCLUDE  =  2

# stock tape

# time
# year month day hour minute second
TIME_YEAR = 0
TIME_MONTH = 1
TIME_DAY = 2
TIME_HOUR = 3
TIME_MINUTE = 4
TIME_SECOND = 5

'''
function
  cmp
  get_stair_format
  get_terminal_size
  is_leap_year
  get_date_duration
  get_time_str
  get_date
  get_weekday
  date_valid
  date_compare
  date_list_to_str
  form_chart_list
  format_list
  join_path
  print_list
  join_list
  merge_list
  colume
  choose_file_from_dir
  get_url_type
  parse_href_url
  change_format
  schedule
  open_file
  sleep
  clear
  mrandom
  random_choose
  norm_file_name
  play_music
  stop_processing
  currency_exchange_ratio
'''

def cmp(a, b):
    if a > b:
        return 1
    elif a == b:
        return 0
    else:
        return -1

# return stair format string,
# is_tail stands for one stair last one
# level is a list stands for which level for stair
# stair_len is for stair charactor number
def get_stair_format(level, is_tail, stair_len = 4):
    rstr = ''
    for clevel in level:
        if clevel == 0:
            rstr = '{0}{1}'.format(rstr, ' ' * stair_len)
        else:
            rstr = '{0}{1}{2}'.format(rstr, '│', ' ' * (stair_len - 1))
    if is_tail:
        rstr = '{0}{1} '.format(rstr, '└─')
    else:
        rstr = '{0}{1} '.format(rstr, '├─')
    return rstr

# return terminal width and height
def get_terminal_size():
    height, width = os.popen('stty size', 'r').read().split()
    return int(height), int(width)

# check if a year is leap year
def is_leap_year(year):
    if year % 4:
        return False
    elif year % 100:
        return True
    elif year % 400:
        return False
    else:
        return True

# get duration
def get_date_duration():
    finished = False
    while not finished:
        log.VLOG('print a date duration (xxxx.xx.xx~yyyy.yy.yy/\d year/\d month/\d week)')
        log.VLOG('\tor insert "n/q" to cancel')
        date_range = mio.stdin()
        if re.match('^\d+ year$', date_range):
            day = common.YEAR_DAY * int(re.search('(\d+)', date_range).group(1))
            start = get_date(-day)
            end = get_date()
        elif re.match('^\d+ month$', date_range):
            day = common.MONTH_DAY * int(re.search('(\d+)', date_range).group(1))
            start = get_date(-day)
            end = get_date()
        elif re.match('^\d+ week$', date_range):
            day = common.WEEK_DAY * int(re.search('(\d+)', date_range).group(1))
            start = get_date(-day)
            end = get_date()
        elif re.match('^\d{4}\.\d{2}\.\d{2}~\d{4}\.\d{2}\.\d{2}$', date_range):
            start = list(map(int, date_range.split('~')[0].split('.')))
            end = list(map(int, date_range.split('~')[1].split('.')))
            if not date_valid(start) or not date_valid(end) or not date_compare(start, end) == LESS:
                log.VLOG('insert date invalid')
                continue
        elif date_range in common.CMD_QUIT:
            start = []
            end = []
        else:
            log.VLOG('not support this type')
            continue
        finished = True
    if len(start) is not 0 and len(end) is not 0:
        log.VLOG('strategy date range:{start} to {end}'.format(
                 start = ' '.join(list(map(str, start))),
                 end = ' '.join(list(map(str, end)))))
    return [start, end]

# return current time, str format
def get_time_str(start, end, spliter):
    if start < TIME_YEAR:
        start = TIME_YEAR
    if end > TIME_SECOND:
        end = TIME_SECOND
    if end < start:
        end = start
    times = list(map(str, time.localtime()[start : end+1]))
    for n,each in enumerate(times):
        if len(each) is 1:
            times[n] = '0' + each
    return spliter.join(times)

# return target date offset delta date
# if targe date is empty, return current date offset
# if delta date is empty, return current date
# filter is list to filter target weekday 0~6 
def get_date(delta_date = 0, current_date = None, filt = None):
    str_format = False
    if not current_date:
        current_date = datetime.now()
    else:
        if isinstance(current_date, str) and re.match('^\d+\.\d+(\.\d+)?$', current_date):
            str_format = True
            current_date = list(map(int, current_date.split('.')))
        current_date = datetime(*current_date)

    finished = False
    while not finished:
        date_target = current_date + timedelta(days = delta_date)
        date = list(map(int, str(date_target).split()[0].split('-')))
        date_str = '.'.join(['0' + str(x) if x < 10 else str(x) for x in date])
        if filt is not None and get_weekday(date_str) in filt:
            delta_date = delta_date + 1 if delta_date > 0 else delta_date - 1
        else:
            finished = True
    if str_format:
        return date_str
    return date

# return weekday of a day(str): xxxx.xx.xx
def get_weekday(date):
    date_list = list(map(int, date.split('.')))
    return datetime(*date_list).weekday() 

# check if date is valid, date format is list [xxxx, xx, xx]
def date_valid(date):
    (year, month, day) = date
    if month is 2:
        if is_leap_year(year) and day > 29:
            return False
        elif not is_leap_year(year) and day > 28:
            return False
        else:
            return True
    elif month in _SOLAR_MONTH:
        if day > 30:
            return False
        else:
            return True
    elif month in _LUNAR_MONTH:
        if day > 31:
            return False
        else:
            return True
    else:
        return False

# date1 and data2 format list [xxxx, xx, xx] / [xxxx, xx] / [xxxx]
# -2: included by
# -1: less than
#  0: equal
#  1: larger than
#  2: include
def date_compare(date1, date2):
    if isinstance(date1, str) and re.match('^\d+\.\d+(\.\d+)?$', date1):
        date1 = list(map(int, date1.split('.')))
    if isinstance(date2, str) and re.match('^\d+\.\d+(\.\d+)?$', date2):
        date2 = list(map(int, date2.split('.')))
    diff = [0] * 3
    diff[0] = cmp(date1[0], date2[0])
    diff[1] = cmp(date1[1], date2[1]) if len(date1) > 1 and len(date2) > 1 else \
              EQUAL if len(date1) == len(date2) else \
              INCLUDED if len(date1) > len(date2) else \
              INCLUDE
    diff[2] = cmp(date1[2], date2[2]) if len(date1) > 2 and len(date2) > 2 else \
              EQUAL if len(date1) == len(date2) else \
              INCLUDED if len(date1) > len(date2) else \
              INCLUDE
    return diff[0] if diff[0] else \
           diff[1] if diff[1] else \
           diff[2]

# convert list data into str, xxxx.xx.xx format
def date_list_to_str(date):
    date_str = str(date[0])
    if len(date) > 1:
        date_str += '.0' + str(date[1]) if date[1] < 10 else '.' + str(date[1])
    if len(date) > 2:
        date_str += '.0' + str(date[2]) if date[2] < 10 else '.' + str(date[2])
    return date_str

# form list to a x * y chart
# offset stands for print front blank, if num per line is 0, auto form
# if list string is true return list string, else return formed list and seg_len pair
def form_chart_list(target_list, list_str = False, offset = 0, num_per_line = 0, sep_len = 4):
    terminal_width = get_terminal_size()[1] - offset - _TERMINAL_BUFFER
    thread_line_num = 10
    max_seg_len = 24 if terminal_width > 24 else terminal_width
    min_seg_len = max_seg_len // 2
    if not isinstance(target_list, list) or len(target_list) == 0:
        return '' if list_str else [], 0
    if num_per_line == 0:
        # get number per line
        segs_len = int(mmath.mean([len(x) for x in target_list]) * 2)
        if segs_len < min_seg_len:
            segs_len = min_seg_len 
        if segs_len > max_seg_len:
            segs_len = max_seg_len 
        num_per_line = terminal_width // (segs_len + sep_len)
        if num_per_line == 0:
            num_per_line = 1
        if len(target_list) // num_per_line <= thread_line_num:
            for num in range(num_per_line - 1, (num_per_line // 2), -1):
                if len(target_list) % num == 0 and len(target_list) // num < 2 * thread_line_num:
                    num_per_line = num
                    break
    segs_len = terminal_width // num_per_line - sep_len
    if segs_len > max_seg_len:
        segs_len = max_seg_len
    chart_list = []
    cur_line = []
    for n, seg in enumerate(target_list):
        if n and n % num_per_line == 0:
            chart_list.append(cur_line)
            cur_line = []
        cur_line.append(seg)
    if len(cur_line) != 0:
        chart_list.append(cur_line)
    if not list_str:
        return chart_list, segs_len
    # return list str
    chart_str_list = []
    for chart_line in chart_list:
        list_str = ''
        for seg in chart_line:
            if len(seg) > segs_len:
                seg = ''.join([seg[:segs_len - 3], '...'])
            list_str += '{0:>{1}s} '.format(seg, segs_len)
        chart_str_list.append(list_str)
    return chart_str_list

# format list, change up down to target sign
def format_list(target_list):
    formated_list = target_list[:]
    for i in range(len(formated_list)):
        if formated_list[i] == common.UP_KEY:
            formated_list[i] = common.UP_SIGN
        if formated_list[i] == common.DOWN_KEY:
            formated_list[i] = common.DOWN_SIGN
        if formated_list[i] == common.LEFT_KEY:
            formated_list[i] = common.LEFT_SIGN
        if formated_list[i] == common.RIGHT_KEY:
            formated_list[i] = common.RIGHT_SIGN
    return formated_list

# join path
def join_path(path_list):
    return os.path.join(*path_list)

# format print lists according to elements in list
# num_per_line if is 0, will print auto
def print_list(target_list, offset = 0, num_per_line = 0, sep_len = 4):
    formated_list = format_list(target_list)
    chart_list = form_chart_list(formated_list, list_str = True, offset = offset, num_per_line = num_per_line, sep_len = sep_len)
    for list_line in chart_list:
        log.INFO(list_line)

def join_list(target_list, sep = ' '):
    return sep.join(list(map(str, target_list)))

def delete_duplicate(origin):
    return [list(y) for y in list(set([tuple(x) for x in origin]))]

# join target list to origin list, cell not contained
def merge_list(origin, target):
    output = origin[:]
    for n, i in enumerate(target):
        schedule(n + 1, len(target))
        if i not in output:
            output.append(i)
    return output

def colume(in_list, col):
    if not in_list or not isinstance(in_list[0], list) or len(in_list[0]) <= col:
        return []
    return [x[col] for x in in_list]

def choose_file_from_dir(target_dir, print_log = True):
    files = os.listdir(target_dir)
    return mio.choose_command(files, print_log = print_log)

# return type of a url
def get_url_type(url):
    return re.sub('://.*', '', url)

# return a combined url from the href and root url
def parse_href_url(href, root_url):
    if href[0] == '/':
        return re.sub('(?<!:)/+', '/', root_url + href)
    else:
        return href

def change_format(data, form):
    if form == common.TYPE_STRING:
        return str(data)
    elif form == common.TYPE_FLOAT:
        return float(data)
    elif form == common.TYPE_INT:
        return int(data)
    else:
        log.INFO('format error: {}'.format(form))
        return data

# print schedule of current job, num should count from 1 to total
def schedule(num, total):
    if int(num / float(total) * 10000) > int((num - 1) / float(total) * 10000):
        percent = int(num / float(total) * 10000) / 100.0
        # print '%s %.2f%% (%d/%d)' % (('%%-%ds' % _SCHEDULE_LEN) % (int(_SCHEDULE_LEN * percent / 99) * '='), percent, num, total),
        log.INFO('\r%s %.2f%% (%d/%d)' % ('%s%s' % (int(_SCHEDULE_LEN * percent / 100) * '>', (_SCHEDULE_LEN - int(_SCHEDULE_LEN * percent / 100)) * '='), percent, num, total), end = False)
        # flush()

# open file for write
# if not exist, create one
def open_file(file_name):
    if re.search('/', file_name):
        file_dir = re.search('(.*)/', file_name).group(1)
        if not os.path.isdir(file_dir):
            os.makedirs(file_dir)
    fp = open(file_name, 'w')
    return fp

# sleep time
def sleep(t):
    time.sleep(t)

# clear screan
def clear():
    os.system('clear')

# random number
def mrandom(threshould = 1):
    return threshould * random.random()

# random choose one from list
def random_choose(choose_list):
    if len(choose_list) == 0:
        return ''
    x = int(mrandom(len(choose_list)))
    return choose_list[x]

# norm file name to transfer ' ', '(', ')' and so on
def norm_file_name(file_name):
    file_name = re.sub(' ', '\ ', file_name)
    file_name = re.sub('\(', '\(', file_name)
    file_name = re.sub('\)', '\)', file_name)
    return file_name

# play a music
def play_music(music_name, background = True):
    exec_cmd = 'play {}'.format(norm_file_name(music_name))
    if background:
        exec_cmd = '{} > log1 2>&1 &'.format(exec_cmd)
    os.system(exec_cmd)

# stop a processing based on command or pid or others
def stop_processing(pid = None, command = None):
    if pid is not None:
        os.system('kill -9 {}'.format(pid))
    elif command is not None:
        pids = psutil.pids()
        for pid in pids:
            p = psutil.Process(pid)
            if p.name() == command:
                os.system('kill -9 {}'.format(pid))

def currency_exchange_ratio(bank, currency):
    url = 'http://data.bank.hexun.com/other/cms/foreignexchangejson.ashx?callback=ShowDatalist'
    proxy_pool = proxypool.ProxyPool()
    page = proxy_pool.get_page(url, common.URL_WRITE)
    exchange_data = page[page.find('['):-1][2:-2].split('},{')
    for data in exchange_data:
        data_dict = dict()
        items = data.split(',')
        for item in items:
            segs = item.split(':')
            key = segs[0]
            value = segs[1][1:-1]
            data_dict[key] = value
        if data_dict['bank'] == bank and data_dict['currency'] == currency:
            return data_dict
    return dict()
