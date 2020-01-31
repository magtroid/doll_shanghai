#!/usr/bin/env python
# coding=utf-8
'''tools for time methods

Magtroid @ 2019-11-12 14:49
'''

# import library
import config
import log
import time
import tools

timers = dict()

def TIMER_BEGIN(name):
    if name not in timers:
        timers[name] = Timer()
    timers[name].begin()

def TIMER_END(name):
    if name not in timers:
        return
    timers[name].end()

def DISPLAY_TIMER():
    time_all = 0.0
    for key, value in timers.items():
        time_all += value.times()
    for key, value in timers.items():
        log.VLOG()
        log.VLOG('{}: {}s {:.2f}%'.format(key, value.times(), value.times() * 100 / time_all))
        

class Timer(object):
    '''
    public:
      begin
      end
      times
    private:
    '''

    def __init__(self):
        self.__time = 0.0

    def begin(self):
        self.__btime = time.time()

    def end(self):
        self.__time += time.time() - self.__btime

    def times(self):
        return self.__time

def main():
    n = 10000
    for i in range(n):
        TIMER_BEGIN('text')
        tools.schedule(i + 1, n)
        TIMER_END('text')
        TIMER_BEGIN('loop')
        for j in range(10000):
            continue
        TIMER_END('loop')

    DISPLAY_TIMER()

if __name__ == '__main__':
    main()

