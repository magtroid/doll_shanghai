#!/usr/bin/env python
# coding=utf-8
'''util for thread pool and processing methods
Magtroid @ 2017-12-04 11:09
'''

# import library
import sys
sys.path.append('..')

import threading
import log

# functions
'''
test_function
is_function
'''

def test_function(count = [0]):
    log.INFO('Hello World {} in thread {}'.format(count[0], threading.current_thread().getName()))
    count[0] += 1

def is_function(func):
    return hasattr(func, '__call__')
