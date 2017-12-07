#!/usr/bin/env python
# coding=utf-8
'''tools for processing pool methods
Magtroid @ 2017-11-22 20:47
'''

# import library
import multiprocessing
import util
import time

class ProcessingPool(object):
    def __init__(self, process_num):
        self.__processing_pool = multiprocessing.Pool(processes = process_num)
        # self.__result = []  # TODO
    def process(self, func, args = None, kwargs = None):
        self.__args = args or []
        self.__kwargs = kwargs or {}
        if util.is_function(func):
            result = self.__processing_pool.apply_async(func, self.__args, self.__kwargs)
            # self.__result.append(result.get())
    def close(self):
        self.__processing_pool.close()
    def join(self):
        self.__processing_pool.join()
    # def result(self):
    #     return self.__result
    # def __getstate__(self):
    #     self_dict = self.__dict__.copy()
    #     del self_dict[_PROCESSING_POOL_NAME]
    #     return self_dict
    # def __setstate__(self, state):
    #     self.__dict__.update(state)

# for test
class a(object):
    def __init__(self):
        self.__a = 10
    def func(self, a, b):
        print('{} {} {}'.format(self.__a, a, b))
        return self.__a

class b(object):
    def __init__(self):
        self.__b = a()

    def func(self, a, time = 12):
        self.__b.func(a, time)

def work(tes, time = 133):
    print(tes)
    print(time)

if __name__ == '__main__':
    pool = ProcessingPool(3)
    c = b()
    # pool = multiprocessing.Pool(processes = 2)
    for i in range(5):
        msg = 'hello {}'.format(i)
        # pool.apply_async(work, [i], {'time' : 12})
        pool.process(c.func, args = [i], kwargs = {'time' : i + 2})
    # print ('-' * 20)
    pool.close()
    pool.join()
    # print pool.result()
    print('sub-process done')
