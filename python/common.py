#!/usr/bin/env python
# coding=utf-8
'''types definition

Magtroid @ 2017-08-01 14:58
'''
from enum import Enum

# write page after get page
URL_WRITE = '__write__'
# read exist page local, if not exist get page
URL_READ = '__read__'
# read exist page local, if not exist continue
URL_READ_THROUGH = '__read_through__'
# url exist
URL_EXIST = '__url_exists__'

# html parser
HTML_PARSER = 'html.parser'
# href key
HREF_KEY = 'href'
# find none
FIND_NONE = -1
# None string
NONE = '__none__'

# empty key
EMPTY_KEY = ''
# backspace key
BACKSPACE_KEY = '\n'

# enum month
class Month(Enum):
    Jan = 1
    Feb = 2
    Mar = 3
    Apr = 4
    May = 5
    Jun = 6
    Jul = 7
    Aug = 8
    Sep = 9
    Oct = 10
    Nov = 11
    Dec = 12

# month day
WEEK_DAY = 7
MONTH_DAY = 30
YEAR_DAY = 365
