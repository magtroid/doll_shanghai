#!/usr/bin/env python
# coding=utf-8
'''
class for context area
Magtroid @ 2019-05-09 17:10
'''

import canvas_config

import area
import log
from define import *

class ContextArea(area.Area):
    '''
    public:
      paint
      erase
      get_coord
      get_context
      display
    private:
      __paint
      __erase
      __context_add
      __update_coordinate
    '''

    def __init__(self, struct = None):
        super().__init__(struct = struct)
        self.__context = []
        self.__coord = []
        self.__erase()

    # add context into target name canvas, coord is [y, x]
    def paint(self, context, coord = None):
        if coord is None:
            coord = self.__coord
        contexts = context.split(BACKSPACE_KEY)
        self.__paint(contexts[0], coord)
        for i in range(1, len(contexts)):
            new_coord = [coord[COORD_Y] + i, 0]
            self.__paint(contexts[i], new_coord)

    # erase contexts
    def erase(self):
        self.__erase()

    # return coordinate for format to insert
    def get_coord(self):
        return self.__coord[:]

    def get_context(self):
        return self.__context[:]

    def display(self):
        for context in self.__context:
            log.VLOG(context)

    def __paint(self, context, coord):
        y, x = coord
        if y < self.struct()[COORD_Y]:
            self.__context[y] = self.__context_add(self.__context[y], context, x)
        self.__update_coordinate(len(context), coord)

    def __erase(self):
        self.__context = [' ' * self.struct()[COORD_X] for y in range(self.struct()[COORD_Y])]
        self.__coord = [0, 0]

    # add b to a in offset, but not overflow a length
    def __context_add(self, a, b, offset):
        if offset >= len(a):
            return a
        begin = offset
        end = min(len(a), begin + len(b))
        result = '{pre_text}{context}{after_text}'.format(
                pre_text = a[:begin],
                context = b[:end - begin],
                after_text = a[end:])
        return result

    def __update_coordinate(self, length, coord):
        if coord[COORD_Y] == self.__coord[COORD_Y]:
            self.__coord[COORD_X] = max(self.__coord[COORD_X], coord[COORD_X] + length)
        elif coord[COORD_Y] > self.__coord[COORD_Y]:
            self.__coord[COORD_Y] = coord[COORD_Y]
            self.__coord[COORD_X] = length

if __name__ == '__main__':
    context_area = ContextArea([10, 20])
    context_area.paint('hello world\n')
    context_area.paint('hello world')
    context_area.display()
