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

# main class
class CANVAS(object):
    # public:
    #   new_area
    #   display_area
    #   paint
    #   display
    #   clear
    # private:
    #   __cover

    def __init__(self, vlog = 0):
        if isinstance(vlog, log.VLOG):
            self.__vlog = vlog
        else:
            self.__vlog = log.VLOG(vlog)
        self._canvas = []
        self.__coordinate = [0, 0]
        self.__area_list = []

    # line stands for area begining line, default 0
    # struct is a list, each 3 params pair(a, x, y) stands for a x * y square at point a
    def new_area(self, struct, line = 0):
        self.__area_list.append(AREA(struct, line = line, vlog = self.__vlog))

    def display_area(self):
        for area in self.__area_list:
            area.display_struct()

    # add context into canvas
    def paint(self, context, backspace = False, coordinate = None):
        if not isinstance(context, str):
            context = str(context)
        if coordinate is None:
            coordinate = self.__coordinate[:]
        envelop_len = coordinate[_COORD_X] + len(context)
        while len(self._canvas) <= coordinate[_COORD_Y]:
            self._canvas.append('')
        self._canvas[coordinate[_COORD_Y]] = '{0}{1}{2}{3}'.format(self._canvas[coordinate[_COORD_Y]][:coordinate[_COORD_X]],
                                                                   ' ' * (coordinate[_COORD_X] - len(self._canvas[coordinate[_COORD_Y]])),
                                                                   context,
                                                                   self._canvas[coordinate[_COORD_Y]][envelop_len:])
        if envelop_len > self.__coordinate[_COORD_X]:
            self.__coordinate[_COORD_X] = envelop_len
        if self.__coordinate[_COORD_Y] == coordinate[_COORD_Y]:
            if backspace:
                self.__coordinate[_COORD_Y] += 1
                self.__coordinate[_COORD_X] = 0

    # clear screan and display canvas
    def display(self):
        tools.clear()  # TODO
        for area in self.__area_list:
            self.__cover(area)

        for canvas_line in self._canvas:
            self.__vlog.VLOG(canvas_line)

    # clear canvas to empty
    def clear(self):
        self._canvas = []
        self.__coordinate = [0, 0]

    # using target canvas cover current canvas 
    def __cover(self, cover_canvas):
        struct, canvas = cover_canvas.get_struct(), cover_canvas.get_canvas()

_OFFSET = 0
_YARRAY = 1
_XARRAY = 2

# vise class
class AREA(CANVAS):
    # public:
    #   frame
    #   get_struct
    #   get_canvas
    #   display_struct
    # private:
    #   __paint
    def __init__(self, struct, line = 0, vlog = 0):
        super(AREA, self).__init__(vlog = vlog)
        if isinstance(vlog, log.VLOG):
            self.__vlog = vlog
        else:
            self.__vlog = log.VLOG(vlog)
        self.__frame_symbol = '*'
        self.__line = line
        self.__struct = struct
        self.__paint()

    # draw frame of current area
    def frame(self):
        self.display()

    def get_struct(self):
        return self.__struct

    def get_canvas(self):
        return self._canvas

    # display structure
    def display_struct(self):
        # self.__vlog.VLOG(self.__struct)
        self.display()

    def __paint(self):
        offset = 0
        line_off = 0
        for n, struct in enumerate(self.__struct):
            for y in range(struct[_YARRAY]):
                line_str = "{}".format("_" * struct[_XARRAY])
                self.paint(line_str, BACKSPACE, [self.__line + y + line_off, struct[_OFFSET] + offset])
            if n == 0:
                offset = self.__struct[0][0]
            line_off += struct[_YARRAY]

# debug test
if __name__ == common.MAIN:
    canvas = CANVAS()
    canvas.paint('fefdfeffedf', BACKSPACE)
    canvas.paint('fefdfeffedf', BACKSPACE)
    canvas.paint('fefdfeffedf', BACKSPACE)
    canvas.paint('fefdfeffedf', BACKSPACE)
    canvas.new_area([[3, 3, 3], [1, 2, 2], [0, 4, 4]])
    canvas.new_area([[15, 3, 3], [0, 4, 4], [0, 4, 4]])
    canvas.display()
