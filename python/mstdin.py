#!/usr/bin/env python
# coding=utf-8
'''tools for stdin methods
Magtroid @ 2017-12-04 17:07
'''

# import library
import sys
import tty
import termios

import config
import threadpoolmanager

# common defin
_STDIN_NAME = '__stdin__'

_DELETE_BOT = '\x7f'

_stdin = ['']

# function
'''
_swallow
get_stdin
'''

# use a list to update stdin dynamic
def _swallow(strs):
    tty_fd = sys.stdin.fileno()
    tty_old_settings = termios.tcgetattr(tty_fd)
    tty.setcbreak(tty_fd)
    try:
        while True:
            char = sys.stdin.read(1)
            strs[0] += char
    finally:
        termios.tcsetattr(tty_fd, termios.TCSADRAIN, tty_old_settings)

def clear_stdin():
    _stdin[0] = ''

def get_stdin():
    return _stdin[0]

threadpoolmanager.new_thread(1, name = _STDIN_NAME)
threadpoolmanager.put_request(_swallow, args = [_stdin], name = _STDIN_NAME)

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
