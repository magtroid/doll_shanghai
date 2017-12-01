#!/usr/bin/env python
# coding=utf-8
'''tools for alarm methods

Magtroid @ 2017-10-31 17:09
'''

# import library
import log
import signal
import sys
import mthreadpool
import time
import tools
import os

# const define
_ALARM_TIME_OUT = 0.01

class MAlarm(object):
    '''
    public:
        is_alive
        result
        stop
        terminate
    private:
        __run  # main function
        __exit
    '''
    def __init__(self, time, func = None, args = None, kwargs = None, rtime = 0):
        self.__time = time
        self.__rtime = rtime
        self.__result = None
        self.__is_alive = True

        self.__clock = mthreadpool.ThreadPool(1, time_out = _ALARM_TIME_OUT)
        self.__func = func if tools.is_function(func) else self.__exit
        self.__args = args or []
        self.__kwargs = kwargs or {}
        self.__rtime = rtime
        self.__req = mthreadpool.WorkRequest(self.__run)
        self.__clock.put_request(self.__req)

    def is_alive(self):
        return self.__is_alive

    def result(self):
        return self.__result

    # stop regression
    def stop(self):
        if self.__func is not None:
            self.__clock.dismiss_all_thread()
        self.__exit()

    # stop by force
    def terminate(self):
        if self.__func is not None:
            self.__clock.terminate_all_thread()
        self.__exit()

    # new thread function
    def __run(self):
        time.sleep(self.__time)
        self.__result = self.__func(*self.__args, **self.__kwargs)
        if self.__rtime:
            self.__clock.put_request(self.__req)
        else:
            self.stop()

    def __exit(self):
        self.__is_alive = False

# for test
def ff(text = [0]):
    while True:
        time.sleep(0.5)
        text[0] += 1
        print 'this is {}'.format(text[0])

if __name__ == '__main__':
    # m = MAlarm(0.5, ff, rtime = 0.5)
    # m = MAlarm(0.5, a.ll, args = [''], rtime = 0.5)
    # n = MAlarm(1, a.jj, args = [''], rtime = 1)
    # a.start()
    # b.start()
    # a.cancel()
    # b.cancel()
    # a = threading.Timer(1, aa)
    # b = threading.Timer(1, bb)
    # a.start()
    # b.start()
    # p = MAlarm(1, a.ll, rtime = 0.5)
    # time.sleep(20)
    # p.stop()
    import mio
    p = MAlarm(1, mio.kbhit)
    import threading
    import time
    while True:
        # print threading._active
        print p.result()
        time.sleep(1)
        pass
