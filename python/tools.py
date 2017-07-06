#!/usr/bin/env python
# coding=utf-8
'''tools for scrap methods

Magtroid @ 2017-06-26 15:58'''

import datetime
import sys

schedule_len = 50

solar_month = [4, 6, 9, 11]
lunar_month = [1, 3, 5, 7, 8, 10, 12]

test_for_write = 'test_write'
test_for_read = 'test_read'

def is_leap_year(year):
    if year % 4:
        return False
    elif year % 100:
        return True
    elif year % 400:
        return False
    else:
        return True

def get_date(*param):
    date = []
    if len(param) is 0:
        delta = 0
    else:
        delta = param[0]

    date_target = datetime.datetime.now() + datetime.timedelta(days=delta)
    date = map(int, str(date_target).split()[0].split('-'))
    return date

def date_valid(date):
    (year, month, day) = date
    if month is 2:
        if is_leap_year(year) and day > 29:
            return False
        elif not is_leap_year(year) and day > 28:
            return False
        else:
            return True
    elif month in solar_month:
        if day > 30:
            return False
        else:
            return True
    elif month in lunar_month:
        if day > 31:
            return False
        else:
            return True
    else:
        return False

# date1 and data2 format xxxx xx xx
def date_compare(date1, date2):
    if not date1[0] == date2[0]:
        if date1[0] > date2[0]:
            return 1
        else:
            return -1
    elif len(date1) is 1 or len(date2) is 1:
        return 0
    else:
        if not date1[1] == date2[1]:
            if date1[1] > date2[1]:
                return 1
            else:
                return -1
        elif len(date1) is 2 or len(date2) is 2:
            return 0
        else:
            if not date1[2] == date2[2]:
                if date1[2] > date2[2]:
                    return 1
                else:
                    return -1
            elif len(date1) is 3 or len(date2) is 3:
                return 0
            else:
                return 0

def schedule(num, total):
    if int(num / float(total) * 10000) > int((num - 1) / float(total) * 10000):
        percent = int(num / float(total) * 10000) / 100.0
        print '\r%s %.2f%% (%d/%d)' % (('%%-%ds' % schedule_len) % (int(schedule_len * percent / 99) * '='), percent, num, total),
        if percent >= 100:
            sys.stdout.flush()
