#!/usr/bin/env python
# coding=utf-8
'''
class for context and format area display
Magtroid @ 2019-05-13 11:30
'''

import canvas_config

import log
from context_area import *
from format_area import *
from define import *

# main class
class Layer(ContextArea, FormatArea):
    '''
    public:
      paint
      display
    private:
      __form_text
    '''
    def __init__(self, struct = None):
        super().__init__(struct = struct)

    def paint(self, context, coord = None, other = '', front = '', back = ''):
        if coord is None:
            coord = self.get_coord()
        contexts = context.split(BACKSPACE_KEY)
        ContextArea.paint(self, contexts[0], coord)
        FormatArea.insert_format(self, coord + [len(contexts[0])], other = other, front = front, back = back)
        for i in range(1, len(contexts)):
            new_coord = [coord[COORD_Y] + i, 0]
            ContextArea.paint(self, contexts[i], new_coord)
            FormatArea.insert_format(self, new_coord + [len(contexts[i])], other = other, front = front, back = back)

    def display(self):
        context = ContextArea.get_context(self)
        format = FormatArea.get_format(self)
        display_text = self.__form_text(context, format)
        for display_line in display_text:
            log.VLOG(display_line)

    def __form_text(self, canvas_context, canvas_format):
        canvas_display = [' ' * self.struct()[COORD_X] for y in range(self.struct()[COORD_Y])]
        for y, iformat in enumerate(canvas_format):
            reverse_format = iformat[:]
            reverse_format.reverse()
            context = canvas_context[y]
            for iform in reverse_format:
                context = '{pre_text}\033[{format}m{format_text}\033[0m{after_text}'.format(
                        pre_text = context[:iform[FORMAT_BEGIN]],
                        format = iform[FORMAT_FORMAT],
                        format_text = context[iform[FORMAT_BEGIN] : iform[FORMAT_END]],
                        after_text = context[iform[FORMAT_END]:])
            canvas_display[y] = context
        return canvas_display

if __name__ == '__main__':
    layer = Layer([10, 20])
    layer.paint('hello world', front = WHITE)
    layer.paint('hello world', coord = [0, 5], front = YELLOW)
    layer.insert_format([2, 5, 10], back = GREEN)
    layer.display()
