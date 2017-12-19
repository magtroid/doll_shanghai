#!/usr/bin/env python
# coding=utf-8
'''tools for canvas print
Magtroid @ 2017-10-17 10:35
'''

# import library
import log
import re
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
# other format
HIGHLIGHT = 'highlight'
UNDERLINE = 'underline'
INVERSE = 'inverse'

_FRONT = '3'
_BACK = '4'

# format format [b, e, c]
_BEGIN = 0
_END = 1
_FORMAT = 2

_WIDTH_BUFF = 4

# move module
MOVE_MODULE_OFF = '__module_off__'
MOVE_MODULE_TO  = '__module_to__'

# main class
class CANVAS(object):
    # public:
    #   new_area
    #   has_area
    #   del_area
    #   move_area
    #   get_area_struct
    #   insert_format
    #   display_area
    #   coordinate
    #   paint
    #   display
    #   clear_area
    #   erase
    # private:
    #   __foundation
    #   __form_text
    #   __cover

    def __init__(self):
        self.__canvas = []
        self.__format = []
        self.__area_dict = dict()
        self.__found = self.__foundation()

    # line stands for area begining line, default 0
    # struct is a list, each 3 params pair(a, x, y) stands for x * y square at point a
    def new_area(self, struct, name, line = 0):
        self.__area_dict[name] = AREA(self.__canvas, self.__format, struct, line = line)

    def has_area(self, name):
        return name in self.__area_dict

    # offset is [y, x] stand for y and x offset, should not move above foundation
    def move_area(self, name, offset, module = MOVE_MODULE_OFF):
        if name in self.__area_dict:
            if module is MOVE_MODULE_TO:
                y, struct = self.__area_dict[name].get_struct()
                x = struct[0][0]
                ioffset = [offset[0] - y, offset[1] - x]
            else:
                ioffset = offset
            self.__area_dict[name].move_struct(ioffset)

    # delete area
    def del_area(self, name):
        if name in self.__area_dict:
            del self.__area_dict[name]

    def get_area_struct(self, name = None):
        if name is None or name == '':
            return self.__found.get_struct()
        if name in self.__area_dict:
            return self.__area_dict[name].get_struct()

    # coord is a list [y, x, l]
    def insert_format(self, coord, other = '', front = '', back = '', name = None):
        if name is None:
            target_area = self.__found
        elif name in self.__area_dict:
            target_area = self.__area_dict[name]
        else:
            return
        target_area.insert_format(coord, other = other, front = front, back = back)

    def display_area(self):
        for area in self.__area_dict:
            area.display_struct()

    def coordinate(self):
        return self.__found.coordinate()

    # add context into canvas
    def paint(self, context, backspace = True, name = None, coordinate = None, other = '', front = '', back = ''):
        if name is None:
            target_area = self.__found
        elif name in self.__area_dict:
            target_area = self.__area_dict[name]
        else:
            return
        target_area.paint(context, backspace, coordinate = coordinate, other = other, front = front, back = back)

    # clear screan and display canvas
    def display(self):
        tools.clear()
        self.erase()
        height, width = tools.get_terminal_size()
        self.__found.update_struct([height, width - _WIDTH_BUFF])
        self.__found.display()
        for key, area in self.__area_dict.items():
            area.display()
        self.__form_text()
        for canvas_line in self.__canvas:
            # log.VLOG(repr(canvas_line))  # FOR DEBUG
            log.VLOG(canvas_line)

    # '' is the foundation key
    # if area_list is none, clear all areas
    def clear_area(self, area_list = None):
        self.__found.clear_area()
        if area_list is None:
            area_list = self.__area_dict.keys()
        elif '' in area_list:
            self.__found.clear_area()
        for iarea in area_list:
            if iarea in self.__area_dict:
                self.__area_dict[iarea].clear_area()

    # clear canvas to empty
    def erase(self):
        self.__canvas[:] = []
        self.__format[:] = []

    # create foundation area cover all screen
    def __foundation(self):
        height, width = tools.get_terminal_size()
        foundation = AREA(self.__canvas, self.__format, [[0, height - 1, width - _WIDTH_BUFF]])
        return foundation

    # get canvas formed by format, if format is None, formed by self.__format
    def __form_text(self, tformat = None):
        if tformat is None:
            tformat = self.__format
        for n, iformat in enumerate(tformat):
            vform = iformat[:]
            vform.reverse()
            text = self.__canvas[n]
            for iform in vform:
                text = u'{0}\033[{1}m{2}\033[0m{3}'.format(text[:iform[_BEGIN]],
                                                           iform[_FORMAT],
                                                           text[iform[_BEGIN]:iform[_END]],
                                                           text[iform[_END]:])
            self.__canvas[n] = text

    # using target canvas cover current canvas 
    def __cover(self, cover_canvas):
        struct, canvas = cover_canvas.get_struct(), cover_canvas.get_canvas()

_FORMAT_SEP = ';'
# struct format [a, y, x]
_OFFSET = 0
_YARRAY = 1
_XARRAY = 2

# unfold struct format [x, l]
_USTOFF = 0
_USTLEN = 1

# sub class
class AREA(object):
    # public:
    #   paint
    #   frame
    #   get_struct
    #   move_struct
    #   get_canvas
    #   insert_format
    #   coordinate
    #   clear
    #   display_struct
    #   update_struct
    #   display
    # private:
    #   __unfold_struct
    #   __form_text
    #   __join_form
    #   __norm_form
    #   __trim_form
    #   __paint
    #   __process_format
    def __init__(self, canvas, cformat, struct, line = 0):
        self.__canvas = canvas
        self.__canvas_format = cformat
        self.__struct = self.__unfold_struct(struct)
        self.__context = [''] * len(self.__struct)
        self.__format = [[]] * len(self.__struct)
        self.__coordinate = [0, 0]
        self.__frame_symbol = '*'
        self.__line = line
        self.__color_pallet = {'black'       : '0',
                               'red'         : '1',
                               'green'       : '2',
                               'yellow'      : '3',
                               'blue'        : '4',
                               'purple'      : '5',
                               'ultramarine' : '6',
                               'white'       : '7',
                               }
        self.__format_pallet = {'highlight'   : '1',
                                'underline'   : '4',
                                'inverse'     : '7',
                                }

    # coordinate is for paint position
    def paint(self, text, backspace = True, coordinate = None, other = '', front = '', back = ''):
        if coordinate is None:
            coordinate = self.__coordinate[:]
        if coordinate[_COORD_Y] >= len(self.__struct):
            return
        while len(self.__context) <= coordinate[_COORD_Y]:
            self.__context.append('')
            self.__format.append([])
            self.__coordinate[_COORD_Y] += 1
            self.__coordinate[_COORD_X] = 0
        self.__context[coordinate[_COORD_Y]] = u'{0}{1}{2}{3}'.format(self.__context[coordinate[_COORD_Y]][:coordinate[_COORD_X]],
                                                                      ' ' * (coordinate[_COORD_X] - len(self.__context[coordinate[_COORD_Y]])),
                                                                      text,
                                                                      self.__context[coordinate[_COORD_Y]][(coordinate[_COORD_X] + len(text)):])
        join_form = self.__join_form(other = other, front = front, back = back)
        if join_form:
            self.__process_format([[coordinate[_COORD_X], coordinate[_COORD_X] + len(text), join_form]],
                                  [coordinate[_COORD_Y], 0, len(text) + coordinate[_COORD_X]])
        if coordinate[_COORD_Y] == self.__coordinate[_COORD_Y]:
            self.__coordinate[_COORD_X] = len(self.__context[self.__coordinate[_COORD_Y]])
            if backspace:
                self.__coordinate[_COORD_Y] += 1
                self.__coordinate[_COORD_X] = 0

    # draw frame of current area
    # def frame(self):
    #     self.display()

    def get_struct(self):
        return self.__line, self.__struct

    # offset is [y, x] stands for y and x array offset
    def move_struct(self, offset):
        self.__line += offset[0]
        if offset[1] != 0:
            for istruct in self.__struct:
                istruct[_USTOFF] += offset[1]

    # def get_canvas(self):
    #     return self.__canvas

    # coord [y, x, l]
    def insert_format(self, coord, other = '', front = '', back = ''):
        join_form = self.__join_form(other = other, front = front, back = back)
        if join_form:
            tformat = [[coord[1], coord[1] + coord[2], join_form]]
            p_coord = [coord[0], self.__struct[coord[0]][_USTOFF], self.__struct[coord[0]][_USTLEN]]
            self.__process_format(tformat, p_coord, append = True)  # TODO

    def coordinate(self):
        return self.__coordinate

    def clear_area(self):
        self.__context[:] = [''] * len(self.__struct)
        self.__format[:] = [[]] * len(self.__struct)
        self.__coordinate = [0, 0]

    # display structure
    # def display_struct(self):
        # log.VLOG(self.__struct)
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
            self.__canvas_format.append([])
        for n, context_line in enumerate(self.__context):
            y = n + self.__line
            x = self.__struct[n][_USTOFF]
            l = self.__struct[n][_USTLEN]
            self.__canvas[y] = u'{0}{1}{2}{3}{4}'.format(self.__canvas[y][:x],
                                                         ' ' * (x - len(self.__canvas[y])),
                                                         context_line[:l],
                                                         ' ' * (l - len(context_line)),
                                                         self.__canvas[y][x + l:])
            self.__process_format(self.__format[n], [y, x, l], pformat_list = self.__canvas_format)

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
                text = u'{0}\033[{1}m{2}\033[0m{3}'.format(text[:iform[_BEGIN]],
                                                           iform[_FORMAT],
                                                           text[iform[_BEGIN]:iform[_END]],
                                                           text[iform[_END]:])
        return text

    def __join_form(self, other = '', front = '', back = ''):
        form = []
        if other in self.__format_pallet:
            form.append(self.__format_pallet[other])
        if front in self.__color_pallet:
            form.append('{}{}'.format(_FRONT, self.__color_pallet[front]))
        if back in self.__color_pallet:
            form.append('{}{}'.format(_BACK, self.__color_pallet[back]))
        return _FORMAT_SEP.join(form)

    def __norm_form(self, pformat):
        format_list = pformat.split(_FORMAT_SEP)
        format_list.reverse()
        nformat = []
        lformat = []
        for iformat in format_list:
            if iformat == '0':
                break
            sign = '0{}'.format(iformat) if len(iformat) == 1 else iformat[0]
            if sign in lformat:
                continue
            else:
                nformat.append(iformat)
                lformat.append(sign)
        rformat = '0' if len(nformat) == 0 else _FORMAT_SEP.join(sorted(nformat, key=lambda d:(len(d), d)))
        return rformat

    def __trim_form(self, text):
        return re.sub('\033\[.*?m(.*?)\033\[0m', '\\1', text)

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

    # set coord_y text format
    # tformat is [[b, e, c]] list stands for target area begin, end and color
    # coord is [y, x, l] stands for canvas y and x array and length
    def __process_format(self, tformat, coord, pformat_list = None, append = True):
        if len(tformat) == 0:
            return
        if pformat_list is None:
            pformat_list = self.__format
        y, x, format_len = coord
        pformat = pformat_list[y]
        tformat_len = max(format_len, tformat[-1][_END]) + x
        max_len = tformat_len if len(pformat) == 0 else max(pformat[-1][_END], tformat_len)
        format_str = ['0'] * max_len
        for iformat in pformat:
            format_str[iformat[_BEGIN] : iformat[_END]] = [iformat[_FORMAT]] * (iformat[_END] - iformat[_BEGIN])
        for iformat in tformat:
            if append == False:
                if iformat[_END] <= format_len:
                    format_str[iformat[_BEGIN] + x : iformat[_END] + x] = [iformat[_FORMAT]] * (iformat[_END] - iformat[_BEGIN])
                elif iformat[_BEGIN] < format_len:
                    format_str[iformat[_BEGIN] + x : format_len + x] = [iformat[_FORMAT]] * (format_len - iformat[_BEGIN])
                else:
                    break
            else:
                if iformat[_END] <= format_len:
                    format_str[iformat[_BEGIN] + x : iformat[_END] + x] = [self.__norm_form('{};{}'.format(z, iformat[_FORMAT])) for z in format_str[iformat[_BEGIN] + x : iformat[_END] + x]]
                elif iformat[_BEGIN] < format_len:
                    format_str[iformat[_BEGIN] + x : format_len + x] = [self.__norm_form('{};{}'.format(z, iformat[_FORMAT])) for z in format_str[iformat[_BEGIN] + x : format_len + x]]
                else:
                    break
        c = '0'
        nformat = []
        cformat = []
        for n, i in enumerate(format_str):
            if i != c:
                if c != '0':
                    nformat.append(cformat)
                cformat = [n, n + 1, i] if i != '0' else []
                c = i
            else:
                if c != '0':
                    cformat[_END] += 1
        if len(cformat) != 0:
            nformat.append(cformat)
        pformat_list[y] = nformat

# debug test
if __name__ == '__main__':
    canvas = CANVAS()
    canvas.erase()
    canvas.clear_area()
    canvas.paint('dfegdefdf')
    canvas.paint('dfegdefdf')
    canvas.paint('dfegdefdf')
    canvas.insert_format([1, 1, 1], front = RED)
    canvas.insert_format([2, 1, 1], other = INVERSE)
    # canvas.insert_format([1, 1, 2], front = BLUE)
    # canvas.insert_format([0, 1, 2], back = RED)
    # canvas.insert_format([1, 1, 2], back = RED)
    # canvas.insert_format([0, 1, 20], BLUE)
    # canvas.new_area([[1, 4, 4], [0, 5, 7]], name = 'cissy')
    # canvas.paint('dfegd', BACKSPACE, name = 'cissy', color = RED)
    # canvas.paint('boobb', BACKSPACE, name = 'cissy', coordinate = [4, 2], color = BLUE)
    # canvas.paint('fejke', BACKSPACE, name = 'cissy', coordinate = [4, 1], color = GREEN)
    # canvas.new_area([[3, 3, 3], [1, 2, 2], [0, 4, 4]], name = 'cissy2')
    # canvas.new_area([[15, 3, 3], [0, 4, 4], [0, 4, 4]], name = 'cissy3')
    canvas.display()
