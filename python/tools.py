#!/usr/bin/env python
# coding=utf-8
'''tools for common tools

Magtroid @ 2017-06-26 15:58
'''

# import library
from datetime import datetime, timedelta
import mmath
import mio
import os
import re
import sys
import time

# const define
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

# function
#   flush
#   lclear
#   refresh_line
#   stdout
#   stdin
#   get_stair_format
#   get_terminal_size
#   is_leap_year
#   get_time_str
#   get_date
#   get_weekday
#   date_valid
#   date_compare
#   date_list_to_str
#   form_chart_list
#   print_list
#   choose_command
#   get_url_type
#   parse_href_url
#   ultra_encode
#   schedule
#   open_file
#   sleep
#   clear

# clear stdout
def flush():
    sys.stdout.flush()

# clear current line
def lclear():
    terminal_width = get_terminal_size()[1]
    print '\r{}\r'.format(' ' * (terminal_width - 1)),

def refresh_line(pstr):
    lclear()
    print pstr,
    flush()

# return stdin
def stdin(block = True, search_list = None):
    rstr = ''
    if not block:
        command = mio.kbhit(block = False)
        if command == '\x1b':
            rstr = 'esc'
        elif command == '\x1b[A':
            rstr = 'up'
        elif command == '\x1b[B':
            rstr = 'down'
        elif command == '\x1b[C':
            rstr = 'right'
        elif command == '\x1b[D':
            rstr = 'left'
        else:
            rstr = command
        return rstr

    if search_list is None:
        search_list = []
    switch_model = False
    while True:
        command = mio.kbhit(block = False)
        if command:
            if command == '\t' or command == '\x1b[Z':
                if not switch_model:
                    if command == '\t':
                        switch_model = True
                        fill_coordinate = [0, 0]
                        fill_list = []
                        for seg in search_list:
                            seg = str(seg)
                            if re.search('^{}'.format(rstr), seg):
                                fill_list.append(seg)
                        fill_chart, segs_len = form_chart_list(fill_list, offset = len(rstr) + 4)
                        if len(fill_chart) != 0:
                            pstr = '{} :'.format(rstr)
                            for n, fill_seg in enumerate(fill_chart[fill_coordinate[0]]):
                                if len(seg) > segs_len:
                                    seg = ''.join([seg[:segs_len - 3], '...'])
                                if n == fill_coordinate[1]:
                                    pstr += '{0:>{1}}* '.format(''.join(['*', fill_seg]), segs_len)
                                else:
                                    pstr += '{0:>{1}}  '.format(fill_seg, segs_len)
                            refresh_line(pstr)
                        else:
                            switch_model = False
                            fill_coordinate = [-1, -1]
                            refresh_line(rstr)
                else:
                    if command == '\t':
                        fill_coordinate[1] += 1
                        if fill_coordinate[1] >= len(fill_chart[fill_coordinate[0]]):
                            fill_coordinate[0] += 1
                            fill_coordinate[1] = 0
                            if fill_coordinate[0] >= len(fill_chart):
                                fill_coordinate[0] = 0
                    else:  # \x1b[Z
                        fill_coordinate[1] -= 1
                        if fill_coordinate[1] < 0:
                            fill_coordinate[0] -= 1
                            if fill_coordinate[0] < 0:
                                fill_coordinate[0] = len(fill_chart) - 1
                            fill_coordinate[1] = len(fill_chart[fill_coordinate[0]]) - 1
                    pstr = '{} :'.format(rstr)
                    for n, fill_seg in enumerate(fill_chart[fill_coordinate[0]]):
                        if len(seg) > segs_len:
                            seg = ''.join([seg[:segs_len - 3], '...'])
                        if n == fill_coordinate[1]:
                            pstr += '{0:>{1}}* '.format(''.join(['*', fill_seg]), segs_len)
                        else:
                            pstr += '{0:>{1}}  '.format(fill_seg, segs_len)
                    refresh_line(pstr)
            elif command == '\n':
                if switch_model:
                    switch_model = False
                    fill_coordinate = [-1, -1]
                    rstr = fill_chart[fill_coordinate[0]][fill_coordinate[1]]
                    refresh_line(rstr)
                else:
                    return rstr
            elif command in ['esc', 'up', 'down', 'left', 'right']:  # arrow
                switch_model = False
                fill_coordinate = [-1, -1]
                refresh_line(rstr)
            elif command == '\x7f':  # backspace
                switch_model = False
                fill_coordinate = [-1, -1]
                rstr = rstr[:-1]
                refresh_line(rstr)
            else:
                switch_model = False
                fill_coordinate = [-1, -1]
                rstr += command
                refresh_line(rstr)

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

# return current time, str format
def get_time_str(start, end, spliter):
    if start < TIME_YEAR:
        start = TIME_YEAR
    if end > TIME_SECOND:
        end = TIME_SECOND
    if end < start:
        end = start
    times = map(str, time.localtime()[start : end+1])
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
            current_date = map(int, current_date.split('.'))
        current_date = datetime(*current_date)

    finished = False
    while not finished:
        date_target = current_date + timedelta(days = delta_date)
        date = map(int, str(date_target).split()[0].split('-'))
        date_str = '.'.join(map(str, date))
        if filt is not None and get_weekday(date_str) in filt:
            delta_date = delta_date + 1 if delta_date > 0 else delta_date - 1
        else:
            finished = True
    if str_format:
        return date_str
    return date

# return weekday of a day(str): xxxx.xx.xx
def get_weekday(date):
    date_list = map(int, date.split('.'))
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
        date1 = map(int, date1.split('.'))
    if isinstance(date2, str) and re.match('^\d+\.\d+(\.\d+)?$', date2):
        date2 = map(int, date2.split('.'))
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
    terminal_width = get_terminal_size()[1] - offset
    thread_line_num = 10
    max_seg_len = 24 if terminal_width > 24 else terminal_width
    min_seg_len = max_seg_len / 2
    if not isinstance(target_list, list) or len(target_list) == 0:
        return '' if list_str else [], 0
    if num_per_line == 0:
        # get number per line
        segs_len = int(mmath.mean([len(x) for x in target_list]) * 2)
        if segs_len < min_seg_len:
            segs_len = min_seg_len 
        if segs_len > max_seg_len:
            segs_len = max_seg_len 
        num_per_line = terminal_width / (segs_len + sep_len)
        if num_per_line == 0:
            num_per_line = 1
        if len(target_list) / num_per_line <= thread_line_num:
            for num in range(num_per_line - 1, (num_per_line / 2), -1):
                if len(target_list) % num == 0 and len(target_list) / num < 2 * thread_line_num:
                    num_per_line = num
                    break
    segs_len = terminal_width / num_per_line - sep_len
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

# format print lists according to elements in list
# num_per_line if is 0, will print auto
def print_list(target_list, offset = 0, num_per_line = 0, sep_len = 4):
    chart_list = form_chart_list(target_list, list_str = True, offset = offset, num_per_line = num_per_line, sep_len = sep_len)
    for list_line in chart_list:
        print list_line

# get command
# if input choose, select the key of choose
# if not blocked, receive only one character
def choose_command(choose = None, option = None, block = True, log = True):
    if choose:
        if isinstance(choose, dict):
            choose_item = map(str, choose.keys())
        elif isinstance(choose, list):
            choose_item = choose
        else:
            print 'not support this format of command {}'.format(choose)
            return
        if log:
            print 'choose your items: \n or press "cancel" or "q" to quit'
            print_list(choose_item)
        command = stdin(search_list = choose_item, block = block)
        while command.split(':')[0] not in choose:
            if command == 'cancel' or command == 'q':
                return command
            else:
                print 'error items, type again'
                command = stdin(search_list = choose_item, block = block)
    else:
        print 'type your items or press "cancel" or "q" to quit'
        command = stdin()
    return command

# return type of a url
def get_url_type(url):
    return re.sub('://.*', '', url)

# return a combined url from the href and root url
def parse_href_url(href, root_url):
    if href[0] == '/':
        return re.sub('(?<!:)/+', '/', root_url + href)
    else:
        return href

# ultra encode for special page
def ultra_encode(text_in):
    uni = unicode(text_in)
    text_out = ''
    for s in uni:
        string = str(s)
        if string[0] == '\xc3':
            if string[1] == '\xa1':
                text_out += '\xe1'
            elif string[1] == '\xa2':
                text_out += '\xe2'
            elif string[1] == '\xa3':
                text_out += '\xe3'
            elif string[1] == '\xa4':
                text_out += '\xe4'
            elif string[1] == '\xa5':
                text_out += '\xe5'
            elif string[1] == '\xa6':
                text_out += '\xe6'
            elif string[1] == '\xa7':
                text_out += '\xe7'
            elif string[1] == '\xa8':
                text_out += '\xe8'
            elif string[1] == '\xa9':
                text_out += '\xe9'
            elif string[1] == '\xaa':
                text_out += '\xea'
            elif string[1] == '\xab':
                text_out += '\xeb'
            elif string[1] == '\xac':
                text_out += '\xec'
            elif string[1] == '\xad':
                text_out += '\xed'
            elif string[1] == '\xae':
                text_out += '\xee'
            elif string[1] == '\xaf':
                text_out += '\xef'
        elif string[0] == '\xc2':
            text_out += string[1]
        else:
            text_out += string
    return text_out

# print schedule of current job
def schedule(num, total):
    if int(num / float(total) * 10000) > int((num - 1) / float(total) * 10000):
        percent = int(num / float(total) * 10000) / 100.0
        # print '%s %.2f%% (%d/%d)' % (('%%-%ds' % _SCHEDULE_LEN) % (int(_SCHEDULE_LEN * percent / 99) * '='), percent, num, total),
        print '\r%s %.2f%% (%d/%d)' % ('%s%s' % (int(_SCHEDULE_LEN * percent / 100) * '>', (_SCHEDULE_LEN - int(_SCHEDULE_LEN * percent / 100)) * '='), percent, num, total),
        flush()

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
