#!/usr/bin/env python
# coding=utf-8
'''Module for log print

Magtroid @ 2017-08-15 11:00
method for log manager
'''

# import library
import common

# common define
_LEVEL = 0

def set_log_level(level):
    _LEVEL = int(level)

# static function
def INFO(log = None, end = True):
    if log is None:
        log = ''
    if end:
        print(log)
    else:
        print(log),

def VLOG(log = None, level = 0, end = True):
    if _LEVEL >= level:
        INFO(log, end = end)

if __name__ == common.MAIN:
    _LEVEL = 3
    INFO()
    INFO('hello')
    VLOG()
    VLOG('Hello', 1)
    VLOG('Hello', 2)
