#!/usr/bin/env python
# coding=utf-8
'''tools for thread pool methods
Magtroid @ 2017-11-20 16:18
'''

# import library
import os
import sys
import threadpool_config
import ctypes
import queue
import threading
import time

import log
import util

# common define
_STATUS_SLEEP = '__sleep__'
_STATUS_WORKING = '__working__'
_STATUS_DISMISS = '__dismiss__'
_STATUS_LIST = [_STATUS_SLEEP, _STATUS_WORKING, _STATUS_DISMISS]

_NAME_BASE = '__base__'

_DEFAULT_TIME_OUT = 3
_TERMINAL_TIME_OUT = 0.01

class NoResultsPending(Exception):
    '''all requests have been processed'''
    pass

# thread class
class WorkThread(threading.Thread):
    '''
    public:
        get_status
        get_id
        get_tid
        get_time_out
        get_thread
        run  # main function
        dismiss
        awake
        terminate
    private:
        __update_status
        __update_tid
    '''
    def __init__(self, request_queue, result_queue, thread_id, time_out = _DEFAULT_TIME_OUT):
        threading.Thread.__init__(self)
        self.__request_queue = request_queue
        self.__result_queue = result_queue
        self.__thread_id = thread_id
        self.__time_out = time_out
        self.__status = _STATUS_SLEEP
        self.__tid = None
        self.setDaemon(True)
        self.start()

    # sleep working dismiss
    def get_status(self):
        return self.__status

    def get_id(self):
        return self.__thread_id

    def get_tid(self):
        return self.__tid

    def get_time_out(self):
        return self.__time_out

    def get_thread(self):
        return self

    def run(self):
        self.__update_tid()
        while True:
            if self.__status == _STATUS_DISMISS:
                break
            try:
                request = self.__request_queue.get(True, self.__time_out)
            except queue.Empty:
                continue
            else:
                if self.__status == _STATUS_DISMISS:
                    self.__request_queue.put(request)
                    break
                try:
                    self.__update_status(_STATUS_WORKING)
                    result = request.run_function()
                    self.__result_queue.put((request, result))
                    self.__update_status(_STATUS_SLEEP)
                except:
                    self.__result_queue.put((request, sys.exc_info()))
                    self.__update_status(_STATUS_SLEEP)

    def dismiss(self):
        self.__status = _STATUS_DISMISS

    def awake(self):
        self.__status = _STATUS_SLEEP

    def terminate(self):
        if self.__tid in threading._active:
            log.VLOG('terminate tid {}'.format(self.__tid), 0)
            if self.__status is _STATUS_WORKING:
                ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(self.__tid), ctypes.py_object(SystemExit))
            self.dismiss()

    def __update_status(self, status):
        if self.__status != _STATUS_DISMISS and status in _STATUS_LIST:
            self.__status = status

    def __update_tid(self):
        for tid, tobj in threading._active.items():
            if tobj is self:
                self.__tid = tid
                break

# request class
class WorkRequest(object):
    '''
    public:
        request_id
        run_function
        run_call_back
    private:
        __exit
    '''
    def __init__(self, func = None, args = None, kwargs = None, request_id = None,
                 call_back = None, cargs = None, ckwargs = None):
        if request_id is None:
            self.__request_id = id(self)
        else:
            try:
                self.__request_id = hash(request_id)
            except TypeError:
                raise TypeError('request id must be hashable')
        self.__func = func if util.is_function(func) else self.__exit
        self.__call_back = call_back if util.is_function(call_back) else None
        self.__args = args or []
        self.__kwargs = kwargs or {}
        self.__cargs = cargs or []
        self.__ckwargs = ckwargs or {}

    def __str__(self):
        return 'WorkRequest id = {id} function = {function} kargs = {args} wargs = {kwargs}'.format(
                id = self.__request_id,
                function = self.__func,
                args = self.__args,
                kwargs = self.__kwargs)

    def request_id(self):
        return self.__request_id

    def run_function(self):
        res = self.__func(*self.__args, **self.__kwargs)
        return res

    def run_call_back(self, result):
        if self.__call_back is not None:
            return self.__call_back(result, *self.__cargs, **self.__ckwargs)
        return None

    def __exit(self):
        sys.exit()

# main class
class ThreadPool(object):
    '''
    public:
        thread_pool_status
        thread_number
        new_thread
        dismiss_thread
        terminate_thread
        put_request
        poll_response
    private:
        __update_time_out
    '''
    # time out is thread pool request time out, usually is max time of all threads
    def __init__(self, thread_num = 0, name = _NAME_BASE, time_out = 0):
        self.__request_queue = queue.Queue()
        self.__result_queue = queue.Queue()
        self.__thread_pool = []
        self.__work_requests = dict()
        self.__name = name
        self.__time_out = time_out
        self.new_thread(thread_num, time_out = self.__time_out)

    # sleep or working
    def thread_pool_status(self):
        status = _STATUS_SLEEP
        for thread in self.__thread_pool:
            if thread.get_status() == _STATUS_WORKING:
                status = _STATUS_WORKING
                break
        return status

    def thread_number(self, detail = False):
        if detail:
            for thread in self.__thread_pool:
                log.VLOG('\tname: {:20s} id: {:2d} status: {:10s} time_out: {:3f} tid: {}'.format(self.__name,
                                                                                                  thread.get_id(),
                                                                                                  thread.get_status(),
                                                                                                  thread.get_time_out(),
                                                                                                  thread.get_thread()))
        return len(self.__thread_pool)

    # new thread with id from 0 to range
    # return thread id list of initialed new thread
    def new_thread(self, thread_number, time_out = _DEFAULT_TIME_OUT):
        thread_fund_id = self.thread_number()
        new_thread_id_list = []
        for i in range(thread_number):
            new_thread = WorkThread(self.__request_queue, self.__result_queue, thread_id = thread_fund_id + i, time_out = time_out)
            self.__thread_pool.append(new_thread)
            new_thread_id_list.append(new_thread.get_tid())
        self.__time_out = max(time_out, self.__time_out)
        return new_thread_id_list

    # stop target thread, if number is 0, stop all
    def dismiss_thread(self, number = 0, do_join = False, time_out = None):
        dismiss_list = []
        if number == 0:
            number = self.thread_number()
        for i in range(min(number, self.thread_number())):
            thread = self.__thread_pool[i]
            thread.dismiss()
            dismiss_list.append(thread)
        if do_join:
            if time_out is None:
                time_out = self.__time_out
            for thread in dismiss_list:
                thread.join(time_out)
        self.__update_time_out()

    def terminate_thread(self, number = 0):
        if number == 0:
            number = self.thread_number()
        for i in range(min(number, self.thread_number())):
            thread = self.__thread_pool.pop()
            thread.terminate()
            thread.join(_TERMINAL_TIME_OUT)
        self.__update_time_out()

    # request is WorkRequest class
    def put_request(self, request, block = True):
        assert isinstance(request, WorkRequest)
        self.__request_queue.put(request, block)
        self.__work_requests[request.request_id()] = request

    def poll_response(self, block = False):
        while True:
            if not self.__work_requests:
                break
            try:
                request, result = self.__result_queue.get(block = block)
                request.run_call_back(result)
                del self.__work_requests[request.request_id()]
            except queue.Empty:
                time.sleep(self.__time_out)

    # update time out to max thread time out
    def __update_time_out(self):
        time_out = 0
        for thread in self.__thread_pool:
            time_out = max(time_out, thread.get_time_out())
        self.__time_out = time_out

# for test
class do(object):
    def __init__(self, a):
        self.__b = a
    def do_work(self):
        time.sleep(0.5)
        self.__b += 3
        print('thread: {} print {}'.format(threading.current_thread().getName(), self.__b))
        if self.__b % 2 == 0:
            return True
        else:
            return False
    def call_back(self, result):
        ty = 'odd' if not result else 'even'
        print('this number {} is {}'.format(self.__b, ty))

def call_back(result, do):
    do.call_back(result)

def loop():
    try:
        while True:
            pass
    finally:
        print('pass')

def looop():
    n = ThreadPool(1)
    req = WorkRequest(loop)
    n.put_request(req)
    time.sleep(1)
    begin = time.time()
    thread_num = len(threading._active)
    n.terminate_all_thread()
    while len(threading._active) == thread_num:
        pass
    end = time.time()

def play():
    os.system('play heroes/music/Tavern-Inferno.mp3')

if __name__ == '__main__':
    a = ThreadPool(1)
    req = WorkRequest(play)
    a.put_request(req)
    # a.put_request(req)
    # a.put_request(req)
    # a.put_request(req)
    time.sleep(1)
    # thread_num = len(threading._active)
    # n = 1
    # while True:
    #     n += 1
    #     print(threading._active)
    #     time.sleep(1)
    #     if n is 5:
    #         a.terminate_thread()
    #     elif n is 10:
    #         break
    #     pass
    print('done')
