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

_COORD_Y = 0
_COORD_X = 1

# color
BLACK = 'black'
RED   = 'red'
GREEN = 'green'
YELLOW = 'yellow'
BLUE = 'blue'
PURPLE = 'purple'
ULTRAMARINE = 'ultramarine'
WHITE = 'white'

# main class
class CANVAS(object):
    # public:
    #   new_area
    #   get_area_struct
    #   display_area
    #   coordinate
    #   paint
    #   display
    #   clear_area
    #   erase
    # private:
    #   __foundation
    #   __cover

    def __init__(self, vlog = 0):
        if isinstance(vlog, log.VLOG):
            self.__vlog = vlog
        else:
            self.__vlog = log.VLOG(vlog)
        self.__canvas = []
        self.__coordinate = [0, 0]
        self.__area_dict = dict()
        self.__found = self.__foundation()

    # line stands for area begining line, default 0
    # struct is a list, each 3 params pair(a, x, y) stands for x * y square at point a
    def new_area(self, struct, name, line = 0):
        self.__area_dict[name] = AREA(self.__canvas, struct, line = line, vlog = self.__vlog)

    def get_area_struct(self, name):
        if name in self.__area_dict:
            return self.__area_dict[name].get_struct()

    def display_area(self):
        for area in self.__area_dict:
            area.display_struct()

    def coordinate(self):
        return self.__coordinate

    # add context into canvas
    def paint(self, context, backspace = True, name = None, coordinate = None, color = ''):
        if name is None:
            target_area = self.__found
        elif name in self.__area_dict:
            target_area = self.__area_dict[name]
        else:
            return
        target_area.paint(context, backspace, coordinate = coordinate, color = color)

    # clear screan and display canvas
    def display(self):
        tools.clear()
        height, width = tools.get_terminal_size()
        self.__found.update_struct([height, width])
        self.__found.display()
        for key, area in self.__area_dict.items():
            area.display()
        for canvas_line in self.__canvas:
            self.__vlog.VLOG(canvas_line)

    # '' is the foundation key
    # if area_list is none, clear all areas
    def clear_area(self, area_list = None):
        self.__found.clear_area()
        if area_list is None:
            area_list = self.__area_dict.keys()
        elif '' in area_list:
            self.__found.clear_area()
        for iarea in area_list:
            if iarea in self.__area_dict():
                self.__area_dict[iarea].clear_area()

    # clear canvas to empty
    def erase(self):
        self.__canvas[:] = []
        self.__coordinate = [0, 0]

    # create foundation area cover all screen
    def __foundation(self):
        height, width = tools.get_terminal_size()
        foundation = AREA(self.__canvas, [[0, height - 1, width]], vlog = self.__vlog)
        return foundation

    # using target canvas cover current canvas 
    def __cover(self, cover_canvas):
        struct, canvas = cover_canvas.get_struct(), cover_canvas.get_canvas()

# struct format [a, y, x]
_OFFSET = 0
_YARRAY = 1
_XARRAY = 2

# format format [b, e, c]
_BEGIN = 0
_END = 1
_COLOR = 2

# unfold struct format [x, l]
_USTOFF = 0
_USTLEN = 1

# sub class
class AREA(object):
    # public:
    #   paint
    #   frame
    #   get_struct
    #   get_canvas
    #   clear
    #   display_struct
    #   update_struct
    #   display
    # private:
    #   __unfold_struct
    #   __form_text
    #   __paint
    #   __process_format
    def __init__(self, canvas, struct, line = 0, vlog = 0):
        if isinstance(vlog, log.VLOG):
            self.__vlog = vlog
        else:
            self.__vlog = log.VLOG(vlog)
        self.__canvas = canvas
        self.__struct = self.__unfold_struct(struct)
        self.__context = [''] * len(self.__struct)
        self.__format = [[]] * len(self.__struct)
        self.__coordinate = [0, 0]
        self.__frame_symbol = '*'
        self.__line = line
        self.__pallet = {'black'       : '30',
                         'red'         : '31',
                         'green'       : '32',
                         'yellow'      : '33',
                         'blue'        : '34',
                         'purple'      : '35',
                         'ultramarine' : '36',
                         'white'       : '37',}

    # coordinate is for paint position
    def paint(self, text, backspace = True, coordinate = None, color = ''):
        text = str(text)
        if coordinate is None:
            coordinate = self.__coordinate[:]
        if coordinate[_COORD_Y] >= len(self.__struct):
            return
        while len(self.__context) <= coordinate[_COORD_Y]:
            self.__context.append('')
            self.__format.append([])
            self.__coordinate[_COORD_Y] += 1
            self.__coordinate[_COORD_X] = 0
        self.__context[coordinate[_COORD_Y]] = '{0}{1}{2}{3}'.format(self.__context[coordinate[_COORD_Y]][:coordinate[_COORD_X]],
                                                                     ' ' * (coordinate[_COORD_X] - len(self.__context[coordinate[_COORD_Y]])),
                                                                     text,
                                                                     self.__context[coordinate[_COORD_Y]][(coordinate[_COORD_X] + len(text)):])
        if color in self.__pallet:
            self.__process_format(coordinate[_COORD_Y],
                                  [coordinate[_COORD_X], coordinate[_COORD_X] + len(text), self.__pallet[color]])
        if coordinate[_COORD_Y] == self.__coordinate[_COORD_Y]:
            self.__coordinate[_COORD_X] = len(self.__context[self.__coordinate[_COORD_Y]])
            if backspace:
                self.__coordinate[_COORD_Y] += 1
                self.__coordinate[_COORD_X] = 0

    # draw frame of current area
    # def frame(self):
    #     self.display()

    def get_struct(self):
        return self.__struct

    # def get_canvas(self):
    #     return self.__canvas

    def clear_area(self):
        self.__context[:] = []
        self.__format[:] = []
        self.__coordinate = [0, 0]

    # display structure
    # def display_struct(self):
        # self.__vlog.VLOG(self.__struct)
        # self.display()

    # TODO update found to single area
    def update_struct(self, struct):
        nstruct = []
        for i, istruct in enumerate(self.__struct):
            if i < struct[0]:
                nstruct.append([istruct[_USTOFF], struct[1]])
        self.__struct = nstruct

    def display(self):
        while len(self.__canvas) < self.__line + len(self.__context):
            self.__canvas.append('')
        for n, context_line in enumerate(self.__context):
            y = n + self.__line
            x = self.__struct[n][_USTOFF]
            self.__canvas[y] = '{0}{1}{2}{3}{4}'.format(self.__canvas[y][:x],
                                                     ' ' * (x - len(self.__canvas[y])),
                                                     self.__form_text(context_line[:self.__struct[n][_USTLEN]], self.__format[n]),
                                                     ' ' * (self.__struct[n][_USTLEN] - len(context_line)),
                                                     self.__canvas[y][self.__struct[n][_USTOFF] + self.__struct[n][_USTLEN]:])

    def __unfold_struct(self, struct):
        ustruct = []
        fstruct = struct[0]
        foffset = fstruct[_OFFSET]
        for line in range(fstruct[_YARRAY]):
            ustruct.append([foffset, fstruct[_XARRAY]])
        for istruct in struct[1:]:
            for line in range(istruct[_YARRAY]):
                ustruct.append([foffset + istruct[_OFFSET], istruct[_XARRAY]])
        return ustruct

    def __form_text(self, text, form):
        vform = form[:]
        vform.reverse()
        for iform in vform:
            if iform[_BEGIN] < len(text):
                text = '{0}\033[{1}m{2}\033[0m{3}'.format(text[:iform[_BEGIN]],
                                                          iform[_COLOR],
                                                          text[iform[_BEGIN]:iform[_END]],
                                                          text[iform[_END]:])
        return text

    def __paint(self):
        offset = 0
        line_off = 0
        for n, struct in enumerate(self.__struct):
            for y in range(struct[_YARRAY]):
                line_str = "{}".format(self.__frame_symbol * struct[_XARRAY])
                self.paint(line_str, BACKSPACE, [self.__line + y + line_off, struct[_OFFSET] + offset])
            if n == 0:
                offset = self.__struct[0][0]
            line_off += struct[_YARRAY]

    # set coord_y text format, tformat is [b, e, c] stands for begin, end and color
    def __process_format(self, coord_y, tformat):
        pformat = self.__format[coord_y]
        max_len = tformat[_END] if len(pformat) == 0 else max(pformat[-1][_END], tformat[_END])
        format_str = [0] * max_len
        for iformat in pformat:
            format_str[iformat[_BEGIN]:iformat[_END]] = [iformat[_COLOR]] * (iformat[_END] - iformat[_BEGIN])
        format_str[tformat[_BEGIN]:tformat[_END]] = [tformat[_COLOR]] * (tformat[_END] - tformat[_BEGIN])
        c = 0
        nformat = []
        for n, i in enumerate(format_str):
            if i != c:
                if c != 0:
                    nformat.append(cformat)
                cformat = [n, n + 1, i] if i != 0 else []
                c = i
            else:
                if c != 0:
                    cformat[_END] += 1
        if len(cformat) != 0:
            nformat.append(cformat)
        self.__format[coord_y] = nformat

# debug test
if __name__ == common.MAIN:
    canvas = CANVAS()
    canvas.erase()
    canvas.paint('fefdfeffedf', BACKSPACE)
    canvas.paint('fefdfeffedf', BACKSPACE)
    canvas.paint('fefdfeffedf', BACKSPACE)
    canvas.paint('fefdfeffedf', BACKSPACE)
    canvas.new_area([[1, 4, 4], [0, 5, 7]], name = 'cissy')
    canvas.paint('dfegd', BACKSPACE, name = 'cissy', color = RED)
    canvas.paint('boobb', BACKSPACE, name = 'cissy', coordinate = [4, 2], color = BLUE)
    canvas.paint('fejke', BACKSPACE, name = 'cissy', coordinate = [4, 1], color = GREEN)
    # canvas.new_area([[3, 3, 3], [1, 2, 2], [0, 4, 4]], name = 'cissy2')
    # canvas.new_area([[15, 3, 3], [0, 4, 4], [0, 4, 4]], name = 'cissy3')
    canvas.display()
