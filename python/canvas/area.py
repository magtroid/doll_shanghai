#!/usr/bin/env python
# coding=utf-8
'''
class for base area
Magtroid @ 2019-05-08 17:38
'''

import canvas_config

import tools

_STRUCT_HEIGHT_BUFFER = 1  # buffer for other command lines print
_STRUCT_WIDTH_BUFFER = 4  # if context contains chinese, it is longer than 1 character in display, and it will overflow to next line

class Area(object):
    '''
    public:
      struct
    private:
      __default_struct
    '''

    def __init__(self, struct = None):
        if struct is None:
            self.__struct = self.__default_struct()
        else:
            self.__struct = struct

    def struct(self):
        return self.__struct[:]

    def __default_struct(self):
        height, width = tools.get_terminal_size()
        return [height - _STRUCT_HEIGHT_BUFFER, width - _STRUCT_WIDTH_BUFFER]

if __name__ == '__main__':
    area = Area([10, 20])
    print(area.struct())
