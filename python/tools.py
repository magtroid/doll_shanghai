#!/usr/bin/env python
# coding=utf-8
'''tools for scrap methods

Magtroid @ 2017-06-26 15:58
'''

# import library
from datetime import datetime, timedelta
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
_TIME_ACCU = 6  # year month day hour minute second

# function
#   is_leap_year
#   get_date
#   get_weekday
#   date_valid
#   date_compare
#   choose_commond
#   get_url_type
#   parse_href_url
#   ultra_encode
#   schedule

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
def get_time_str():
    return ''.join(map(str, time.localtime()[:_TIME_ACCU]))

# return current date offset delta date
# if delta date is empty, return current date
def get_date(delta_date = None):
    date = []
    if not delta_date:
        delta_date = 0

    date_target = datetime.now() + timedelta(days = delta_date)
    date = map(int, str(date_target).split()[0].split('-'))
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

# get commond
# if input choose, select the key of choose
def choose_commond(choose = None, option = None):
    if choose:
        print 'choose your items: %s\n or press "cancel" or "q" to quit' % str(choose.keys()).decode('string_escape')
        commond = sys.stdin.readline().strip()
        while not choose.has_key(commond.split(':')[0]):
            if commond == 'cancel' or commond == 'q':
                return commond
            else:
                print 'error items, type again'
                commond = sys.stdin.readline().strip()
    else:
        print 'type your items or press "cancel" or "q" to quit'
        commond = sys.stdin.readline().strip()
    return commond

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
        # print '\r%s %.2f%% (%d/%d)' % (('%%-%ds' % _SCHEDULE_LEN) % (int(_SCHEDULE_LEN * percent / 99) * '='), percent, num, total),
        print '\r%s %.2f%% (%d/%d)' % ('%s%s' % (int(_SCHEDULE_LEN * percent / 100) * '>', (_SCHEDULE_LEN - int(_SCHEDULE_LEN * percent / 100)) * '='), percent, num, total),
        sys.stdout.flush()
