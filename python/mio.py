#!/usr/bin/env python
# coding=utf-8
'''tools for io methods

Magtroid @ 2017-10-31 11:25
'''

# import library
import common
import malarm
import select
import sys
import termios
import tty

# const define
REST = -1

# function
#   stdin
#   kbhit

# read stdin fp
# number stands for read number of stdin
# if number is 0, read until \n
# if number is REST read rest all if no \n
def stdin(number = 0):
    if number == 0:
        return sys.stdin.readline().strip()
    if number != REST:
        return sys.stdin.read(number)
    m = malarm.MAlarm(0.01)
    rstr = ''
    try:
        while True:
            rstr += stdin(1)
    except:
        pass
    return rstr

# monitor keyboard hit in runing program
# if block, return after each backspace, else return each
def kbhit(block = True):
    rstr = ''
    if block:
        r = select.select([sys.stdin], [], [], 0.01)
        if len(r[0]) > 0:
            rstr = stdin()
    else:
        tty_fd = sys.stdin.fileno()
        tty_old_settings = termios.tcgetattr(tty_fd)
        tty.setcbreak(tty_fd)

        while not select.select([sys.stdin], [], [], 0.01)[0]:
            pass
        rstr = stdin(REST)
        termios.tcsetattr(tty_fd, termios.TCSADRAIN, tty_old_settings)
    return rstr

if __name__ == common.MAIN:
    while True:
        command = kbhit(block = False)
        if command:
            print 'what you type is: ' + repr(command)
            break
