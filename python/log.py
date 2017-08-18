#!/usr/bin/env python
# coding=utf-8
'''Module for log print

Magtroid @ 2017-08-15 11:00
method for log manager
'''

# import library

# main class
class VLOG(object):
    # public:
    #   VLOG
    # private:

    # __level is class log level
    def __init__(self, log_level = 0):
        self.__level = log_level

    # level is current log level
    def VLOG(self, log, level = 0):
        if self.__level >= level:
            print log
