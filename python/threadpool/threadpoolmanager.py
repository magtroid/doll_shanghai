#!/usr/bin/env python
# coding=utf-8
'''singleton for thread pool methods
Magtroid @ 2017-12-05 11:31
'''

# import library
import time
import threading

import mthreadpool
from mthreadpool import _NAME_BASE
import log
import util

# singleton object
# key value is threadpool name and target threadpool
thread_pool_manager = dict()

# function
'''
new_thread
thread_pool_status
thread_number
all_thread_number
dismiss_thread
terminate_thread
dismiss_all_thread
terminate_all_thread
put_request
poll_response
'''

def new_thread(thread_number, name = _NAME_BASE, time_out = 0):
    if name not in thread_pool_manager:
        thread_pool_manager[name] = mthreadpool.ThreadPool(name = name, time_out = time_out)
    thread_pool_manager[name].new_thread(thread_number, time_out = time_out)

def thread_pool_status(name = _NAME_BASE):
    if name in thread_pool_manager:
        return thread_pool_manager[name].thread_pool_status()

def thread_number(name = _NAME_BASE, detail = False):
    if name in thread_pool_manager:
        return thread_pool_manager[name].thread_number(detail = detail)

def all_thread_number(detail = False):
    total_number = 0
    for threadpool in thread_pool_manager.values():
        total_number += threadpool.thread_number(detail = detail)
    if detail:
        log.VLOG('all thread number is {}'.format(total_number))
    return total_number

def dismiss_thread(name = _NAME_BASE, number = 0, do_join = False, time_out = None):
    if name in thread_pool_manager:
        thread_pool_manager[name].dismiss_thread(number = number, do_join = do_join, time_out = time_out)
        if thread_number(name = name) == 0:
            del thread_pool_manager[name]

def terminate_thread(name = _NAME_BASE, number = 0):
    if name in thread_pool_manager:
        thread_pool_manager[name].terminate_thread(number = number)
        if thread_number(name = name) == 0:
            del thread_pool_manager[name]

def dismiss_all_thread():
    for name, threadpool in thread_pool_manager.items():
        threadpool.dismiss_thread(do_join = True)
        del thread_pool_manager[name]

def terminate_all_thread():
    for name, threadpool in thread_pool_manager.items():
        threadpool.terminate_thread()
        del thread_pool_manager[name]

def put_request(func, args = None, kwargs = None,
                call_back = None, cargs = None, ckwargs = None,
                name = _NAME_BASE):
    if util.is_function(func) and name in thread_pool_manager:
        req = mthreadpool.WorkRequest(func, args = args, kwargs = kwargs,
                                      call_back = call_back, cargs = cargs, ckwargs = ckwargs)
        thread_pool_manager[name].put_request(req)

def poll_response(name = _NAME_BASE, block = False):
    if name in thread_pool_manager:
        thread_pool_manager[name].poll_response(block = block)

# for test
def loop():
    try:
        while True:
            pass
    finally:
        print('pass')

if __name__ == '__main__':
    new_thread(1)
    import sys
    put_request(sys.stdin.read)
    # new_thread(2)
    # new_thread(5, name = 'time')
    # new_thread(4, name = 'base')
    # all_thread_number(detail = True)
    # put_request(loop)
    n = 0
    while True:
        n += 1
        time.sleep(1)
        log.INFO(threading._active)
        if n is 3:
            terminate_thread()
    #     if n is 6:
    #         terminate_thread(name = 'base')
    #     if n is 9:
    #         terminate_thread(name = 'time')
        if n is 12:
            break
