#!/usr/bin/env python
# coding=utf-8
'''tools for alarm methods

Magtroid @ 2017-10-31 17:09
'''

# import library
import time

import threadpoolmanager
import log
import util

# const define
_ALARM_TIME_OUT = 0.01
_ALARM_NAME = '__alarm__'

clock_number = 0
def clock_number(i, clocks = [0]):
    clocks[0] += i
    return clocks[0]

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
        clock_num = clock_number(1)
        self.__name = '{}{}'.format(_ALARM_NAME, clock_num)
        self.__clock = threadpoolmanager.new_thread(1, name = self.__name, time_out = _ALARM_TIME_OUT)
        self.__func = func if util.is_function(func) else self.__exit
        self.__args = args or []
        self.__kwargs = kwargs or {}
        threadpoolmanager.put_request(self.__run, args = [self.__time], name = self.__name)

    def is_alive(self):
        return self.__is_alive

    def result(self):
        return self.__result

    # stop regression
    def stop(self):
        if self.__func is not self.__exit:
            threadpoolmanager.dismiss_thread(name = self.__name)
        self.__exit()

    # stop by force
    def terminate(self):
        if self.__func is not self.__exit:
            threadpoolmanager.terminate_thread(name = self.__name)
        self.__exit()

    # new thread function
    def __run(self, ctime):
        time.sleep(ctime)
        self.__result = self.__func(*self.__args, **self.__kwargs)
        if self.__rtime:
            threadpoolmanager.put_request(self.__run, args = [self.__rtime], name = self.__name)
        else:
            self.stop()

    def __exit(self):
        self.__is_alive = False
        clock_number(-1)

# for test
def ff(text = [0]):
    while True:
        time.sleep(0.5)
        text[0] += 1
        print('this is {}'.format(text[0]))

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
    p = MAlarm(1, util.test_function, rtime = 0.1)
    q = MAlarm(1, util.test_function, rtime = 0.1)
    import threading
    import time
    n = 0
    while True:
        # print(threading._active)
        # print(p.result())
        time.sleep(1)
        n += 1
        if n is 5:
            p.terminate()
        if n is 7:
            q.terminate()
        if n is 9:
            break
        pass
