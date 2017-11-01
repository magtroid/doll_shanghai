#!/usr/bin/env python
# coding=utf-8
'''tools for alarm methods

Magtroid @ 2017-10-31 17:09
'''

# import library
import signal
import sys

class MAlarm(object):
    def __init__(self, zzz):
        self.zzz = zzz
        signal.signal(signal.SIGALRM, self.__exit)
        self.start()

    def start(self):
        signal.setitimer(signal.ITIMER_REAL, self.zzz)

    def __exit(self):
        print 'abc'
        sys.exit()
