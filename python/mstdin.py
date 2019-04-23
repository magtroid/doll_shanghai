#!/usr/bin/env python
# coding=utf-8
'''tools for stdin methods
Magtroid @ 2017-12-04 17:07
'''

# import library
import sys
import tty
import termios
import time

import config
import threadpoolmanager
import processingpoolmanager

# common defin
DELTA_TIME = 0.001
_STDIN_NAME = '__stdin__'
_DELETE_BOT = '\x7f'
_stdin = ['']

# function
'''
_swallow
clear_stdin
open_stdin
get_stdin
close_stdin
'''

# use a list to update stdin dynamic
def _swallow(strs):
    tty_fd = sys.stdin.fileno()
    tty_old_settings = termios.tcgetattr(tty_fd)
    tty.setcbreak(tty_fd)
    try:
        while True:
            # while processingpoolmanager.is_locked():
            #     pass
            # threadpoolmanager.set_lock()
            char = sys.stdin.read(1)
            strs[0] += char
            # threadpoolmanager.set_unlock()
            time.sleep(DELTA_TIME)
    finally:
        termios.tcsetattr(tty_fd, termios.TCSADRAIN, tty_old_settings)


def clear_stdin():
    _stdin[0] = ''

# thread should new just before put request, other wise the thread will consume
# lots of cpu resources due to loop in thread
def open_stdin():
    threadpoolmanager.new_thread(1, name = _STDIN_NAME)
    threadpoolmanager.put_request(_swallow, args = [_stdin], name = _STDIN_NAME)

def get_stdin():
    return _stdin[0]

def close_stdin():
    threadpoolmanager.dismiss_thread(name = _STDIN_NAME)


if __name__ == '__main__':
    import time
    import threading
    time.sleep(3)
    threadpoolmanager.terminate_thread(name = _STDIN_NAME)
    n = 0
    while True:
        n += 1
        time.sleep(1)
        print(threading._active)
        if n is 5:
            break
    print(_stdin)
    print('done')
