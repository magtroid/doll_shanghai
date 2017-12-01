#!/usr/bin/env python
# coding=utf-8
'''tools for thread pool methods

Magtroid @ 2017-11-20 16:18
'''

# import library
import common
import ctypes
import log
import Queue
import sys
import threading
import tools
import time

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
        get_time_out
        get_status
        run  # main function
        dismiss
        awake
        terminate
    private:
        __update_status
        __update_pid
    '''
    def __init__(self, request_queue, result_queue, name, thread_id, time_out = _DEFAULT_TIME_OUT):
        threading.Thread.__init__(self)
        self.__request_queue = request_queue
        self.__result_queue = result_queue
        self.__name = name
        self.__thread_id = thread_id
        self.__time_out = time_out
        self.__status = _STATUS_SLEEP
        self.__tid = None
        self.setDaemon(True)
        self.start()

    def get_time_out(self):
        return self.__time_out

    # sleep working dismiss
    def get_status(self):
        return self.__status

    def run(self):
        self.__update_tid()
        while True:
            if self.__status == _STATUS_DISMISS:
                break
            try:
                request = self.__request_queue.get(True, self.__time_out)
            except Queue.Empty:
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
            # print threading.current_thread().getName()
            log.VLOG('terminate tid {}'.format(self.__tid), 0)
            res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(self.__tid), ctypes.py_object(SystemExit))
            print 'terminate status {}'.format(res)
            print threading._active
            t_len = len(threading._active)
            while t_len == len(threading._active):
                pass
            print threading._active

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
                 call_back = None, cargs = None, ckwargs = None, name = None):
        if request_id is None:
            self.__request_id = id(self)
        else:
            try:
                self.__request_id = hash(request_id)
            except TypeError:
                raise TypeError('request id must be hashable')
        self.__func = func if tools.is_function(func) else self.__exit
        self.__call_back = call_back if tools.is_function(call_back) else None
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
        all_thread_number
        new_thread
        dismiss_thread
        terminate_thread
        put_request
        poll
        dismiss_all_thread
        terminate_all_thread
    private:
        __update_time_out
    '''
    # time out is thread pool request time out, usually is max time of all threads
    def __init__(self, thread_num = 0, name = _NAME_BASE, time_out = _DEFAULT_TIME_OUT):
        self.__request_queue = Queue.Queue()
        self.__result_queue = Queue.Queue()
        self.__thread_group = dict()
        self.__work_requests = dict()
        self.__time_out = time_out
        self.new_thread(thread_num, name = name, time_out = self.__time_out)

    # sleep or working
    def thread_pool_status(self):
        status = _STATUS_SLEEP
        for thread_group_item in self.__thread_group.items():
            for thread in thread_group_item[1]:
                if thread.get_status() == _STATUS_WORKING:
                    status = _STATUS_WORKING
                    break
        return status

    # return target name thread, if no target name, return base thread number
    def thread_number(self, name = _NAME_BASE):
        if name in self.__thread_group:
            return len(self.__thread_group[name])

    def all_thread_number(self):
        total_number = 0
        for thread_group in self.__thread_group.keys():
            total_number += self.thread_number(thread_group)
        return total_number

    # new thread is named with name, id from 0 to range
    def new_thread(self, thread_number, name = _NAME_BASE, time_out = _DEFAULT_TIME_OUT):
        if name not in self.__thread_group:
            self.__thread_group[name] = []
        thread_fund_id = self.thread_number(name)
        for i in range(thread_number):
            self.__thread_group[name].append(WorkThread(self.__request_queue, self.__result_queue, name = name, thread_id = thread_fund_id + i, time_out = time_out))
        self.__time_out = max(time_out, self.__time_out)

    # stop target name thread, if no target name, stop base, if number is 0, stop all
    def dismiss_thread(self, name = _NAME_BASE, number = 0, do_join = False, time_out = None):
        if name in self.__thread_group:
            dismiss_list = []
            if number == 0:
                number = self.thread_number(name)
            for i in range(min(number, self.thread_number(name))):
                thread = self.__thread_group[name].pop()
                thread.dismiss()
                dismiss_list.append(thread)
            if do_join:
                if time_out is None:
                    time_out = self.__time_out
                for thread in dismiss_list:
                    thread.join(time_out)
            self.__update_time_out()

    def terminate_thread(self, name = _NAME_BASE, number = 0, do_join = False, time_out = None):
        if name in self.__thread_group:
            if number == 0:
                number = self.thread_number(name)
            for i in range(min(number, self.thread_number(name))):
                thread = self.__thread_group[name].pop()
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
            except Queue.Empty:
                time.sleep(self.__time_out)

    # stop all thread and quit, if check request, 
    def dismiss_all_thread(self, check_request = False):
        if check_request:
            while self.__request_queue.qsize():
                time.sleep(self.__time_out)
        for thread_group in self.__thread_group.keys():
            self.dismiss_thread(thread_group, do_join = True)

    # stop by force
    def terminate_all_thread(self):  # TODO fix this function logistic later
        for thread_group in self.__thread_group.keys():
            self.terminate_thread(thread_group)

    # update time out to max thread time out
    def __update_time_out(self):
        time_out = 0
        for thread_group in self.__thread_group.items():
            for thread in thread_group[1]:
                time_out = max(time_out, thread.get_time_out())
        self.__time_out = time_out

# for test
class do(object):
    def __init__(self, a):
        self.__b = a
    def do_work(self):
        time.sleep(0.5)
        self.__b += 3
        print 'thread: {} print {}'.format(threading.current_thread().getName(), self.__b)
        if self.__b % 2 == 0:
            return True
        else:
            return False
    def call_back(self, result):
        ty = 'odd' if not result else 'even'
        print 'this number {} is {}'.format(self.__b, ty)

def call_back(result, do):
    do.call_back(result)

def loop():
    try:
        while True:
            pass
    finally:
        print 'pass'

def looop():
    n = ThreadPool(1)
    req = WorkRequest(loop)
    n.put_request(req)
    time.sleep(1)
    print threading._active
    begin = time.time()
    thread_num = len(threading._active)
    n.terminate_all_thread()
    print threading._active
    while len(threading._active) == thread_num:
        pass
    print threading._active
    end = time.time()
    print end - begin

if __name__ == common.MAIN:
    # m = ThreadPool(10)
    # x = ThreadPool(9)
    # for i in range(100):
    #     n = do(i)
    #     req = WorkRequest(n.do_work, call_back = call_back, cargs = [n])
    #     m.put_request(req)
    #     x.put_request(req)
    # m.poll()
    # m.stop()
    # x.poll()
    # x.stop()
    m = ThreadPool(1)
    req = WorkRequest(looop)
    m.put_request(req)
    time.sleep(1)
    # print time.time()
    # print threading._active
    # begin = time.time()
    # m.terminate_all_thread()
    thread_num = len(threading._active)
    # while len(threading._active) == thread_num:
    #     pass
    while True:
        pass
    # end = time.time()
    # print threading._active
    # print end - begin
    print 'done'
