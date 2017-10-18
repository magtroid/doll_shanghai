#!/usr/bin/env python
# coding=utf-8
'''tools for canvas print
Magtroid @ 2017-10-17 10:35
'''

# import library
import common
import log
import tools

# common const
BACKSPACE = True

# main class
class CANVAS(object):
    # public:
    #   paint
    #   display
    #   clear
    # private:

    def __init__(self, vlog = 0):
        self.__vlog = log.VLOG(vlog)
        self.__canvas = ''

    # add context into canvas
    def paint(self, context, backspace = False):
        self.__canvas += context
        if backspace:
            self.__canvas += common.BACKSPACE_KEY

    # clear screan and display canvas
    def display(self):
        tools.clear()
        self.__vlog.VLOG(self.__canvas)

    # clear canvas to empty
    def clear(self):
        self.__canvas = ''
