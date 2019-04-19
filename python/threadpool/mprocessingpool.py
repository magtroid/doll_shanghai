#!/usr/bin/env python
# coding=utf-8
'''tools for processing pool methods
Magtroid @ 2017-11-22 20:47
'''

# import library
import multiprocessing
import util
import time

# common define

class ProcessingPool(object):
    def __init__(self, process_num):
        self.__processing_pool = multiprocessing.Pool(processes = process_num)
        self.__processing_num = process_num
        self.__result = []
    def process(self, func, args = None, kwargs = None):
        self.__args = args or []
        self.__kwargs = kwargs or {}
        if util.is_function(func):
            result = self.__processing_pool.apply_async(func, self.__args, self.__kwargs)
            self.__result.append(result)

    def processing_number(self):
        return self.__processing_num

    def close(self):
        self.__processing_pool.close()
    def get_result(self):
        return self.__result
    def terminate(self):
        self.__processing_pool.terminate()
    def join(self):
        self.__processing_pool.join()

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

def play():
    os.system('play heroes/music/Tavern-Inferno.mp3')

if __name__ == '__main__':
    pool = ProcessingPool(1)
    pool.process(play)
    print(pool.pid())
    pool.close()
    pool.join()
    # c = b()
    # # pool = multiprocessing.Pool(processes = 2)
    # for i in range(5):
    #     msg = 'hello {}'.format(i)
    #     # pool.apply_async(work, [i], {'time' : 12})
    #     pool.process(c.func, args = [i], kwargs = {'time' : i + 2})
    # # print ('-' * 20)
    # pool.close()
    # try:
    #     pool.process(c.func, args = [i], kwargs = {'time' : i + 2})
    # except:
    #     print('closed')
    # pool.join()
    # # print pool.result()
    print('sub-process done')
