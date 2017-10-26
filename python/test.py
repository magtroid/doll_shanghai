#!/usr/bin/env python
# coding=utf-8
""" python non blocking input
"""
import sys
import select
from time import sleep
import termios
import tty

# old_settings = termios.tcgetattr(sys.stdin)
tty.setcbreak(sys.stdin.fileno())
while True:
    # if select.select([sys.stdin], [], [], 0.01) == ([sys.stdin], [], []):
    r = select.select([sys.stdin], [], [], 0.01)
    if r:
        print r[0]
        c = sys.stdin.read(1)
        if c == '\n': break
        print repr(c)
        # sys.stdout.write(c)
        # sys.stdout.flush()
# termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
print 'done'
