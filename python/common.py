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
# mandarin length
MAND_LENGTH = 2

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
# enter key
ENTER_KEY = '\n'
# quit command
CMD_QUIT = 'qQnN'
# yes or no command
YON_COMMAND = ['y', 'n']
Y_COMMAND = 'y'
N_COMMAND = 'n'

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

MON = 0
TUE = 1
WED = 2
THU = 3
FRI = 4
SAT = 5
SUN = 6

# month day
WEEK_DAY = 7
MONTH_DAY = 30
YEAR_DAY = 365

UP_KEY = '\x1b[A'
DOWN_KEY = '\x1b[B'
RIGHT_KEY = '\x1b[C'
LEFT_KEY = '\x1b[D'
TAB_KEY = '\t'
SHIFT_TAB_KEY = '\x1b[Z'
UP_SIGN = '↑'
DOWN_SIGN = '↓'
LEFT_SIGN = '←'
RIGHT_SIGN = '→'
F10_KEY = '\x1b[21'
BLANK_KEY = ' '
ESC_KEY = '\x1b'
DELETE_KEY = '\x7f'

# type string
TYPE_STRING = 'string'
TYPE_INT = 'int'
TYPE_FLOAT = 'float'
