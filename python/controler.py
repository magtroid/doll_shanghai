#!/usr/bin/env python
# coding=utf-8
'''Class for data controler

Magtroid @ 2017-08-02 01:32
methods for controler
'''

# import library
import datalib
import log
import signal
import sys

class Controler(object):
    # private
    #   __exit
    def __init__(self, data_lib, vlog = 0):
        self.__vlog = log.VLOG(vlog)
        self.__control_lib = data_lib
        signal.signal(signal.SIGINT, self.__exit)
        signal.signal(signal.SIGTERM, self.__exit)

    def __exit(self, signum, frame):  
        self.__vlog.VLOG('Stoped by user!')
        if not self.__control_lib.get_controler_switch():
            self.__control_lib.write_data_lib()
        sys.exit()         
