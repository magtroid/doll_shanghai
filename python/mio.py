#!/usr/bin/env python
# coding=utf-8
'''tools for io methods

Magtroid @ 2017-10-31 11:25
'''

# import library
import common
import log
import malarm
import mthreadpool
import threading  # TODO
import select
import sys
import termios
import tools
import tty

# const define
_REST = -1
_ALL = 0

class TimeOverError(Exception):
    '''alarm time over'''
    pass

# function
#   _flush
#   _lclear
#   _refresh_line
#   _swallow
#   _get_stdin
#   kbhit
#   stdin
#   choose command

# clear stdout
def _flush():
    sys.stdout.flush()

# clear current line
def _lclear():
    terminal_width = tools.get_terminal_size()[1]
    log.INFO('\r{}\r'.format(' ' * (terminal_width - 1)), end = False)

def _refresh_line(pstr):
    _lclear()
    log.INFO(pstr, end = False)
    _flush()

# read stdin until receive a exception
def _swallow(strs):
    while True:
        strs[0] += _get_stdin(1)
        # tools.test_function()

# read stdin fp
# number stands for read number of stdin
# if number is _ALL, read until \n
# if number is _REST read rest all if no \n
def _get_stdin(number = _ALL):
    if number == _ALL:
        return sys.stdin.readline().strip()
    if number != _REST:
        return sys.stdin.read(number)
    rstr = ['']
    alarm = malarm.MAlarm(0.01)
    swallow = mthreadpool.ThreadPool(1)
    swallow.put_request(mthreadpool.WorkRequest(_swallow, args = [rstr]))
    print threading._active
    while alarm.is_alive():
        pass
    t_num = len(threading._active)
    print threading._active
    swallow.terminate_all_thread()
    # while len(threading._active) == t_num:
        # print threading._active
        # pass
    print threading._active
    return rstr[0]

# monitor keyboard hit in runing program
# thread block until input exist
# if one_hit is True, return after each backspace, else return each
def kbhit(one_hit = True):
    rstr = ''
    readl = _ALL
    if one_hit:
        tty_fd = sys.stdin.fileno()
        tty_old_settings = termios.tcgetattr(tty_fd)
        tty.setcbreak(tty_fd)
        readl = _REST
    while not select.select([sys.stdin], [], [], 0.01)[0]:
        pass
    rstr = _get_stdin(readl)
    if one_hit:
        termios.tcsetattr(tty_fd, termios.TCSADRAIN, tty_old_settings)
    print threading._active
    return rstr

# return stdin
def stdin(block = True, search_list = None):
    rstr = ''
    if not block:
        command = kbhit()
        if command == '\x1b':
            rstr = 'esc'
        elif command == '\x1b[A':
            rstr = 'up'
        elif command == '\x1b[B':
            rstr = 'down'
        elif command == '\x1b[C':
            rstr = 'right'
        elif command == '\x1b[D':
            rstr = 'left'
        else:
            rstr = command
        return rstr

    if search_list is None:
        search_list = []
    switch_model = False
    while True:
        command = kbhit()
        if command:
            if command == '\t' or command == '\x1b[Z':
                if not switch_model:
                    if command == '\t':
                        switch_model = True
                        fill_coordinate = [0, 0]
                        fill_list = []
                        for seg in search_list:
                            seg = str(seg)
                            if re.search('^{}'.format(rstr), seg):
                                fill_list.append(seg)
                        fill_chart, segs_len = tools.form_chart_list(fill_list, offset = len(rstr) + 4)
                        if len(fill_chart) != 0:
                            pstr = '{} :'.format(rstr)
                            for n, fill_seg in enumerate(fill_chart[fill_coordinate[0]]):
                                if len(seg) > segs_len:
                                    seg = ''.join([seg[:segs_len - 3], '...'])
                                if n == fill_coordinate[1]:
                                    pstr += '{0:>{1}}* '.format(''.join(['*', fill_seg]), segs_len)
                                else:
                                    pstr += '{0:>{1}}  '.format(fill_seg, segs_len)
                            _refresh_line(pstr)
                        else:
                            switch_model = False
                            fill_coordinate = [-1, -1]
                            _refresh_line(rstr)
                else:
                    if command == '\t':
                        fill_coordinate[1] += 1
                        if fill_coordinate[1] >= len(fill_chart[fill_coordinate[0]]):
                            fill_coordinate[0] += 1
                            fill_coordinate[1] = 0
                            if fill_coordinate[0] >= len(fill_chart):
                                fill_coordinate[0] = 0
                    else:  # \x1b[Z
                        fill_coordinate[1] -= 1
                        if fill_coordinate[1] < 0:
                            fill_coordinate[0] -= 1
                            if fill_coordinate[0] < 0:
                                fill_coordinate[0] = len(fill_chart) - 1
                            fill_coordinate[1] = len(fill_chart[fill_coordinate[0]]) - 1
                    pstr = '{} :'.format(rstr)
                    for n, fill_seg in enumerate(fill_chart[fill_coordinate[0]]):
                        if len(seg) > segs_len:
                            seg = ''.join([seg[:segs_len - 3], '...'])
                        if n == fill_coordinate[1]:
                            pstr += '{0:>{1}}* '.format(''.join(['*', fill_seg]), segs_len)
                        else:
                            pstr += '{0:>{1}}  '.format(fill_seg, segs_len)
                    _refresh_line(pstr)
            elif command == '\n':
                if switch_model:
                    rstr = fill_chart[fill_coordinate[0]][fill_coordinate[1]]
                    switch_model = False
                    fill_coordinate = [-1, -1]
                    _refresh_line(rstr)
                else:
                    return rstr
            elif command in ['esc', 'up', 'down', 'left', 'right']:  # arrow
                switch_model = False
                fill_coordinate = [-1, -1]
                _refresh_line(rstr)
            elif command == '\x7f':  # backspace
                switch_model = False
                fill_coordinate = [-1, -1]
                rstr = rstr[:-1]
                _refresh_line(rstr)
            else:
                switch_model = False
                fill_coordinate = [-1, -1]
                rstr += command
                _refresh_line(rstr)

# get command
# if input choose, select the key of choose
# if not blocked, receive only one character
def choose_command(choose = None, option = None, block = True, log = True):
    if choose:
        if isinstance(choose, dict):
            choose_item = map(str, choose.keys())
        elif isinstance(choose, list):
            choose_item = choose
        else:
            log.INFO('not support this format of command {}'.format(choose))
            return
        if log:
            log.INFO('choose your items: \n or press "cancel" or "q" to quit')
            tools.print_list(choose_item)
        command = stdin(search_list = choose_item, block = block)
        while command.split(':')[0] not in choose:
            if command == 'cancel' or command == 'q':
                return command
            else:
                log.INFO('error items, type again')
                command = stdin(search_list = choose_item, block = block)
    else:
        if log:
            log.INFO('type your items or press "cancel" or "q" to quit')
        command = stdin(block = block)
    return command

def dfd():
    command = kbhit()
    if command:
        log.INFO('what you type is: {}'.format(repr(command)))

if __name__ == common.MAIN:
    import time
    import threading
    while True:
        command = kbhit()
        # command1 = kbhit()
        # command2 = kbhit()
        log.INFO('what you type is: {}'.format(repr(command)))
        # log.INFO('what you type is: {} {}'.format(repr(command1), repr(command2)))
        print threading._active
        break
        # a = malarm.MAlarm(0.2, kbhit)
        # time.sleep(0.2)
        # if a.result():
        #     print repr(a.result())
        #     break
