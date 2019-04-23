#!/usr/bin/env python
# coding=utf-8
'''Module for log print

Magtroid @ 2017-08-15 11:00
method for log manager
'''

# import library

# common define
_LEVEL = 0

def set_log_level(level):
    _LEVEL = int(level)

# static function
def INFO(log = None, end = True, ostr = None):
    if log is None:
        log = ''
    if end:
        if ostr is None:
            print(log)
        else:
            ostr += '{}\n'.format(log)
            return ostr
    else:
        if ostr is None:
            print(log, end = '')
        else:
            ostr += '{}'.format(log)
            return ostr

def VLOG(log = None, level = 0, end = True, ostr = None):
    if _LEVEL >= level:
        ostr = INFO(log, end = end, ostr = ostr)
        return ostr

if __name__ == '__main__':
    _LEVEL = 3
    INFO()
    INFO('hello')
    VLOG()
    VLOG('Hello', 1)
    VLOG('Hello', 2)
