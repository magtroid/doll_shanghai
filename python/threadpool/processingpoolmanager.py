#!/usr/bin/env python
# coding=utf-8
'''singleton for processing pool methods
Magtroid @ 2017-12-08 19:56
'''

# import library
import os
import time
import psutil

import mprocessingpool
import threadpoolmanager
import log
import util

# common define
_NAME_BASE = '__base__'

# singleton object
# key value is processing pool name and target processing pool
processing_pool_manager = dict()
processing_pool_lock = [False]

# function
'''
new_processing
set_lock
set_unlock
is_locked
get_pool_status
processing_number
all_processing_number
close_processing
close_all_processing
dismiss_processing
dismiss_all_processing
put_request
'''

def new_processing(process_number, name = _NAME_BASE):
    if name not in processing_pool_manager:
        message = False
        while threadpoolmanager.is_locked():
            if not message:
                log.INFO('wait for processing')
                message = True
            pass
        set_lock()
        processing_pool_manager[name] = mprocessingpool.ProcessingPool(process_number)
        set_unlock()

def set_lock():
    processing_pool_lock[0] = True
def set_unlock():
    processing_pool_lock[0] = False
def is_locked():
    return processing_pool_lock[0]

def get_pool_status():
    return processing_pool_status

def processing_number(name = _NAME_BASE, detail = False):
    if name in processing_pool_manager:
        processing_num = processing_pool_manager[name].processing_number()
        if detail:
            log.VLOG('\t{:20s} {:4d}'.format(name, processing_num))
        return processing_num

def all_processing_number(detail = False):
    total_number = 0
    for name, processing_pool in processing_pool_manager.items():
        total_number += processing_number(name = name, detail = detail)
    if detail:
        log.VLOG('total number is: {:4d}'.format(total_number))
    return total_number

def close_processing(number = 0, name = _NAME_BASE):
    if name in processing_pool_manager:
        left_number = processing_number(name) - number if number != 0 else 0
        temp_processing_pool = processing_pool_manager[name]
        del processing_pool_manager[name]
        if left_number > 0:
            new_processing(left_number, name = name)
        temp_processing_pool.close()
        temp_processing_pool.join()

def close_all_processing(result = False):
    processing_result = []
    for name, processing_pool in list(processing_pool_manager.items()):
        processing_pool.close()
        processing_pool.join()
        del processing_pool_manager[name]
        if result:
            processing_result.extend(processing_pool.get_result())
    return [result.get() for result in processing_result]

def dismiss_processing(name = _NAME_BASE):
    if name in processing_pool_manager:
        origin_number = processing_number(name)
        close_processing(name = name)
        new_processing(origin_number, name = name)

def dismiss_all_processing():
    for name in processing_pool_manager.keys():
        dismiss_processing(name = name)

'''
def terminate_processing(name, number):
def terminate_all_processing():
'''

def put_request(func, args = None, kwargs = None,
                call_back = None, cargs = None, ckwargs = None,
                name = _NAME_BASE):
    if util.is_function(func) and name in processing_pool_manager:
        try:
            processing_pool_manager[name].process(func, args = args, kwargs = kwargs)
        except:
            log.INFO('processing pool {} is not accessable'.format(name))

# for test
def pp():
    close_processing(2)

def play():
    os.system('play heroes/music/Tavern-Inferno.mp3')

def qq():
    for i in range(1):
        put_request(util.test_function, args = [util.PROCESS])

if __name__ == '__main__':
    new_processing(1)
    # new_processing(2, 'function')
    all_processing_number(detail = True)
    # put_request(qq, name = 'function')  # TODO
    put_request(play)
    time.sleep(3)
    # put_request(pp, name = 'function')
    close_all_processing()
    log.INFO('Done')
