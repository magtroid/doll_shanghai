#!/usr/bin/env python
# coding=utf-8
'''util for thread pool and processing methods
Magtroid @ 2017-12-04 11:09
'''

# import library
import threadpool_config
import os

import threading
import log

# const define
THREAD = '__thread__'
PROCESS = '__process__'

# functions
'''
test_function
is_function
'''

def test_function(name = THREAD, count = [0]):
    print('aaa')
    if name == THREAD:
        log.INFO('Hello World {} in thread {}'.format(count[0], threading.current_thread().getName()))
    elif name == PROCESS:
        log.INFO('Hello World {} in process {}'.format(count[0], os.getpid()))
    count[0] += 1

def is_function(func):
    return hasattr(func, '__call__')
