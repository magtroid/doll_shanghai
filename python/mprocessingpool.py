#!/usr/bin/env python
# coding=utf-8
'''tools for processing pool methods

Magtroid @ 2017-11-22 20:47
'''

# import library
import common
import multiprocessing
import time
import tools

# const define
_PROCESSING_POOL_NAME = '_ProcessingPool__processing_pool'

def run(cls, func, args = None, kwargs = None):
    sargs = args or []
    skwargs = kwargs or {}
    if func not in dir(cls):
        func = '_{}{}'.format(cls.__class__.__name__, func)
    cls_func = getattr(cls, func)
    return cls_func(*sargs, **skwargs)

class ProcessingPool(object):
    def __init__(self, process_num):
        self.__processing_pool = multiprocessing.Pool(processes = process_num)
        # self.__result = []  # TODO
    def process(self, func, args = None, kwargs = None):
        self.__args = args or []
        self.__kwargs = kwargs or {}
        if tools.is_function(func):
            result = self.__processing_pool.apply_async(run, (func.__self__, func.__name__, self.__args, self.__kwargs))
            # self.__result.append(result.get())
    def close(self):
        self.__processing_pool.close()
    def join(self):
        self.__processing_pool.join()
    def result(self):
        return self.__result
    def __getstate__(self):
        self_dict = self.__dict__.copy()
        del self_dict[_PROCESSING_POOL_NAME]
        return self_dict
    def __setstate__(self, state):
        self.__dict__.update(state)

# for test
class a(object):
    def __init__(self):
        self.__a = 10
    def __func(self):
        print self.__a
        self.__a += 2
        time.sleep(3)
        print self.__a
        self.__a += 2
        return self.__a

class b(object):
    def __init__(self):
        self.__process_pool = ProcessingPool(3)
        b = a()
        result = []
        b = a()
        for i in range(5):
            msg = 'hello {}'.format(i)
            self.__process_pool.process(self.__func, args = [12, 20])
        print ('-' * 20)
        self.__process_pool.close()
        self.__process_pool.join()
        print self.__process_pool.result()

    def __func(self, a, b):
        print a + b
        time.sleep(3)
        return a * b

if __name__ == common.MAIN:
    # pool = ProcessingPool(3)
    # b = a()
    # result = []
    # b = a()
    # for i in range(5):
    #     msg = 'hello {}'.format(i)
    #     pool.process(b.func)
    # print ('-' * 20)
    # pool.close()
    # pool.join()
    # print pool.result()
    # print ('sub-process done')
    asd = b()
