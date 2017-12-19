#!/usr/bin/env python
# coding=utf-8

import config
import processingpoolmanager

import mstdin

import time
def for_test():
    while True:
        import os
        print('aa')
        print(os.getpid())
        time.sleep(1)
def for_test2():
    while True:
        import os
        print('bb')
        print(os.getpid())
        time.sleep(1)
def for_test3():
    while True:
        import os
        print('cc')
        print(os.getpid())
        time.sleep(1)

class for_t(object):
    def __init__(self):
        processingpoolmanager.new_processing(4)
        processingpoolmanager.processing_number(detail = True)
        pass
    def _for_tes(self):
        print('aa')
    def for_test(self):
        processingpoolmanager.put_request(for_test)
    def for_test2(self):
        processingpoolmanager.put_request(for_test2)
    def for_test3(self):
        processingpoolmanager.put_request(for_test3)
    def close(self):
        processingpoolmanager.close_processing()

time.sleep(1)
a = for_t()
a.for_test()
time.sleep(1)
b = for_t()
b.for_test2()
time.sleep(1)
c = for_t()
c.for_test3()
a.close()
