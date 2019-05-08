#!/usr/bin/env python
# coding=utf-8
'''tools for canvas display
Magtroid @ 2017-10-17 10:35
'''

import canvas_config

# import library
import log
import tools

# debug switch
_FOR_DEBUG = False

# common const
_BACKSPACE_KEY = '\n'

COORD_Y = 0
COORD_X = 1
_COORD_Y = 0
_COORD_X = 1

# color and format defines
_COLORED = True
# color
if _COLORED:
    BLACK = 'black'
    RED   = 'red'
    GREEN = 'green'
    YELLOW = 'yellow'
    BLUE = 'blue'
    PURPLE = 'purple'
    ULTRAMARINE = 'ultramarine'
    WHITE = 'white'
else:
    BLACK = ''
    RED   = ''
    GREEN = ''
    YELLOW = ''
    BLUE = ''
    PURPLE = ''
    ULTRAMARINE = ''
    WHITE = ''
# other format
HIGHLIGHT = 'highlight'
UNDERLINE = 'underline'
TWINKLE = 'twinkle'
INVERSE = 'inverse'
_EMPTY_FORMAT = '0'

_COORD_TYPE = 0
_OTHER = '0'
_FRONT = '3'
_BACK = '4'
_COLOR_PALLET = {'black' : '0',
                 'red' : '1',
                 'green' : '2',
                 'yellow' : '3',
                 'blue' : '4',
                 'purple' : '5',
                 'ultramarine' : '6',
                 'white' : '7'}
_FORMAT_PALLET = {'highlight' : '1',
                  'underline' : '4',
                  'twinkle' : '5',
                  'inverse' : '7'}

_STRUCT_HEIGHT_BUFFER = 1  # buffer for other command lines print
_STRUCT_WIDTH_BUFFER = 4  # if context contains chinese, it is longer than 1 character in display, and it will overflow to next line

_FORMAT_SEP = ';'  # format seperate sign
# process format methods
_PFORMAT_SET = '__set__'
_PFORMAT_APPEND = '__append__'
_PFORMAT_DELETE = '__delete__'

# format coord
_FCOORD_LEN = 2

# format format [begin, end, format]
_FORMAT_BEGIN = 0
_FORMAT_END = 1
_FORMAT_FORMAT = 2

# move canvas coord module
MOVE_MODULE_OFF = '__module_off__'  # move offset coord
MOVE_MODULE_TO  = '__module_to__'  # move to target coord

# main class
class CANVAS(object):
    '''
    public:
      paint
      set_format
      insert_format
      delete_format
      sub_canvas
      del_sub_canvas
      get_context
      get_format
      move_sub_canvas
      display
      erase
      erase_all
      struct
      full
      dump
    private:
      __default_struct
      __paint
      __insert_context
      __set_format
      __insert_format
      __delete_format
      __update_coordinate
      __join_form
      __process_line_format
      __unfold_format_line
      __fold_format_line
      __context_add
      __format_add
      __format_min
      __merge_context
      __merge_format
      __form_text
    '''

    def __init__(self, struct = None):
        if struct is None:
            self.__struct = self.__default_struct()
        else:
            self.__struct = struct
        self.__context = []
        self.__format = []
        self.__coordinate = []
        self.erase()
        self.__sub_canvas_dict = dict()
        self.__sub_canvas_coord = dict()

    # add context into target name canvas, coordinate is [y, x]
    def paint(self, context, name = None, coordinate = None, other = '', front = '', back = ''):
        if name is not None:
            if name in self.__sub_canvas_dict:
                self.__sub_canvas_dict[name].paint(context, coordinate = coordinate, other = other, front = front, back = back)
            return
        if coordinate is None:
            coordinate = self.__coordinate[:]
        contexts = context.split(_BACKSPACE_KEY)
        self.__paint(contexts[0], coordinate, other, front, back)
        for i in range(1, len(contexts)):
            new_coord = [coordinate[_COORD_Y] + i, 0]
            self.__paint(contexts[i], new_coord, other, front, back)

    # coord is a list [y, x, len]
    def set_format(self, coord, other = '', front = '', back = '', name = None):
        if name is not None:
            if name in self.__sub_canvas_dict:
                self.__sub_canvas_dict[name].set_format(coord, other = other, front = front, back = back)
            return
        self.__set_format(coord, other, front, back)

    def insert_format(self, coord, other = '', front = '', back = '', name = None):
        if name is not None:
            if name in self.__sub_canvas_dict:
                self.__sub_canvas_dict[name].insert_format(coord, other = other, front = front, back = back)
            return
        self.__insert_format(coord, other, front, back)

    def delete_format(self, coord, other = '', front = '', back = '', name = None):
        if name is not None:
            if name in self.__sub_canvas_dict:
                self.__sub_canvas_dict[name].delete_format(coord, other = other, front = front, back = back)
            return
        self.__delete_format(coord, other, front, back)

    # struct is [height, width] and coord is [y, x]
    def sub_canvas(self, coord, struct, name):
        if name in self.__sub_canvas_dict:
            return
        self.__sub_canvas_dict[name] = CANVAS(struct)
        self.__sub_canvas_coord[name] = coord[:]

    def del_sub_canvas(self, name):
        if name in self.__sub_canvas_dict:
            del self.__sub_canvas_dict[name]
            del self.__sub_canvas_coord[name]

    def get_context(self):
        return self.__context[:]

    def get_format(self):
        return self.__format[:]

    # offset is [y, x]
    def move_sub_canvas(self, name, offset, module = MOVE_MODULE_OFF):
        if name in self.__sub_canvas_dict:
            if module is MOVE_MODULE_TO:
                self.__sub_canvas_coord[name] = offset
            else:
                coord = self.__sub_canvas_coord[name]
                self.__sub_canvas_coord[name] = [coord[_COORD_Y] + offset[_COORD_Y], coord[_COORD_X] + offset[_COORD_X]]

    # clear screan and display canvas
    def display(self, name = None):
        if name is not None:
            if name in self.__sub_canvas_dict:
                self.__sub_canvas_dict[name].display()
            return
        canvas_context = self.__merge_context()
        canvas_format = self.__merge_format()

        # tools.clear()
        canvas_display = self.__form_text(canvas_context, canvas_format)
        for canvas_line in canvas_display:
            if _FOR_DEBUG:
                log.VLOG(repr(canvas_line))
            else:
                log.VLOG(canvas_line)

    # erase target canvas all contexts and formats
    def erase(self, name = None):
        if name is not None:
            if name in self.__sub_canvas_dict:
                self.__sub_canvas_dict[name].erase()
            return
        self.__coordinate = [0, 0]
        self.__context = [' ' * self.__struct[_COORD_X] for y in range(self.__struct[_COORD_Y])]
        self.__format = [[[0, self.__struct[_COORD_X], _EMPTY_FORMAT]] for y in range(self.__struct[_COORD_Y])]

    # erase current canvas all contexts and formats
    def erase_all(self):
        for name in self.__sub_canvas_dict:
            self.__sub_canvas_dict[name].erase()
        self.erase()

    def struct(self):
        return self.__struct[:]

    def full(self):
        return self.__coordinate[_COORD_Y] >= self.__struct[_COORD_Y]

    # dump target canvas with format
    def dump(self, name = None, other = '', front = '', back = ''):
        if name is not None:
            if name in self.__sub_canvas_dict:
                self.__sub_canvas_dict[name].dump(other = other, front = front, back = back)
            return
        for y in range(len(self.__format)):
            self.__insert_format([y, 0, len(self.__context[y])], other, front, back)

    def __default_struct(self):
        height, width = tools.get_terminal_size()
        return [height - _STRUCT_HEIGHT_BUFFER, width - _STRUCT_WIDTH_BUFFER]

    def __paint(self, context, coordinate, other, front, back):
        if coordinate[_COORD_Y] < self.__struct[_COORD_Y]:
            self.__insert_context(context, coordinate)
            self.__insert_format(coordinate + [len(context)], other, front, back)
        self.__update_coordinate(len(context), coordinate)

    def __insert_context(self, context, coordinate):
        y, x = coordinate
        self.__context[y] = self.__context_add(self.__context[y], context, x)

    # coordinate is [y, x, len]
    def __set_format(self, coordinate, other, front, back):
        joined_form = self.__join_form(other, front, back)
        if joined_form:
            self.__process_line_format(self.__format, coordinate, joined_form, method = _PFORMAT_SET)

    # coordinate is [y, x, len]
    def __insert_format(self, coordinate, other, front, back):
        if coordinate[_COORD_Y] >= self.__struct[_COORD_Y]:
            return
        joined_form = self.__join_form(other, front, back)
        if joined_form:
            self.__process_line_format(self.__format, coordinate, joined_form)

    def __delete_format(self, coordinate, other, front, back):
        joined_form = self.__join_form(other, front, back)
        if joined_form:
            self.__process_line_format(self.__format, coordinate, joined_form, method = _PFORMAT_DELETE)

    def __update_coordinate(self, length, coordinate):
        if coordinate[_COORD_Y] == self.__coordinate[_COORD_Y]:
            self.__coordinate[_COORD_X] = max(self.__coordinate[_COORD_X], coordinate[_COORD_X] + length)
        elif coordinate[_COORD_Y] > self.__coordinate[_COORD_Y]:
            self.__coordinate[_COORD_Y] = coordinate[_COORD_Y]
            self.__coordinate[_COORD_X] = length

    # join target 3 types of forms into 1 string character
    def __join_form(self, other, front, back):
        form_list = []
        if other in _FORMAT_PALLET:
            form_list.append(_FORMAT_PALLET[other])
        if front in _COLOR_PALLET:
            form_list.append('{feature_id}{color_id}'.format(feature_id = _FRONT,
                                                             color_id = _COLOR_PALLET[front]))

        if back in _COLOR_PALLET:
            form_list.append('{feature_id}{color_id}'.format(feature_id = _BACK,
                                                             color_id = _COLOR_PALLET[back]))
        return _FORMAT_SEP.join(form_list)

    # process pformat coord to tformat
    # coord is [y, x, len]
    def __process_line_format(self, pformat, coord, tformat, method = _PFORMAT_APPEND):
        format_line = self.__unfold_format_line(pformat, coord[_COORD_Y])
        if coord[_COORD_X] >= len(format_line):
            return
        begin = coord[_COORD_X]
        end = min(len(format_line), coord[_COORD_X] + coord[_FCOORD_LEN])
        if method == _PFORMAT_APPEND:
            format_line[begin : end] = [self.__format_add(i, tformat) for i in format_line[begin : end]]
        elif method == _PFORMAT_SET:
            format_line[begin : end] = [tformat for i in range(end - begin)]
        elif method == _PFORMAT_DELETE:
            format_line[begin : end] = [self.__format_min(i, tformat) for i in format_line[begin : end]]
        else:
            return
        self.__fold_format_line(pformat, format_line, coord[_COORD_Y])

    # unfold pformat line y
    def __unfold_format_line(self, pformat, y):
        format_line = [_EMPTY_FORMAT for x in range(self.__struct[_COORD_X])]
        for iformat in pformat[y]:
            format_line[iformat[_FORMAT_BEGIN] : iformat[_FORMAT_END]] = [iformat[_FORMAT_FORMAT] for i in range(iformat[_FORMAT_END] - iformat[_FORMAT_BEGIN])]
        return format_line

    # fold format_line to pformat line y
    def __fold_format_line(self, pformat, format_line, y):
        current = _EMPTY_FORMAT
        begin = 0
        end = 0
        result = []
        for n, i in enumerate(format_line):
            if i != current:
                if end > begin:
                    result.append([begin, end, current])
                begin = n
                end = n + 1
                current = i
            else:
                end += 1
        if end > begin:
            result.append([begin, end, current])
        pformat[y] = result[:]

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

    # dict key is format type: front back and use '0' for other, value is target format
    def __format_add(self, a, b):
        type_dict = dict()
        a_list = a.split(_FORMAT_SEP)
        for iformat in a_list:
            if iformat == _EMPTY_FORMAT:
                continue
            # other format type is 0x and front is 3, back is 4
            format_type = '{}{}'.format(_OTHER, iformat[_COORD_TYPE]) if len(iformat) == 1 else iformat[_COORD_TYPE]
            type_dict[format_type] = iformat
        b_list = b.split(_FORMAT_SEP)
        for iformat in b_list:
            if iformat == _EMPTY_FORMAT:
                continue
            # other format type is 0x and front is 3, back is 4
            format_type = '{}{}'.format(_OTHER, iformat[_COORD_TYPE]) if len(iformat) == 1 else iformat[_COORD_TYPE]
            type_dict[format_type] = iformat
        result = _EMPTY_FORMAT if not type_dict else _FORMAT_SEP.join(sorted(type_dict.values(), key = lambda d:(len(d), d)))
        return result

    def __format_min(self, a, b):
        type_dict = dict()
        a_list = a.split(_FORMAT_SEP)
        for iformat in a_list:
            if iformat == _EMPTY_FORMAT:
                continue
            # other format type is 0x and front is 3, back is 4
            format_type = '{}{}'.format(_OTHER, iformat[_COORD_TYPE]) if len(iformat) == 1 else iformat[_COORD_TYPE]
            type_dict[format_type] = iformat
        b_list = a.split(_FORMAT_SEP)
        for iformat in b_list:
            if iformat == _EMPTY_FORMAT:
                continue
            # other format type is 0x and front is 3, back is 4
            format_type = '{}{}'.format(_OTHER, iformat[_COORD_TYPE]) if len(iformat) == 1 else iformat[_COORD_TYPE]
            if format_type in type_dict:
                del type_dict[format_type]
        result = _EMPTY_FORMAT if not type_dict else _FORMAT_SEP.join(sorted(type_dict.values(), key = lambda d:(len(d), d)))
        return result

    def __merge_context(self):
        canvas_context = self.get_context()
        for name in self.__sub_canvas_dict:
            sub_context = self.__sub_canvas_dict[name].get_context()
            sub_coord = self.__sub_canvas_coord[name]
            for i, context in enumerate(sub_context):
                y = i + sub_coord[_COORD_Y]
                x = sub_coord[_COORD_X]
                canvas_context[y] = self.__context_add(canvas_context[y], context, x)
        return canvas_context

    def __merge_format(self):
        canvas_format = self.get_format()
        for name in self.__sub_canvas_dict:
            sub_format = self.__sub_canvas_dict[name].get_format()
            sub_coord = self.__sub_canvas_coord[name]
            for i, lformat in enumerate(sub_format):
                y = i + sub_coord[_COORD_Y]
                x = sub_coord[_COORD_X]
                for iformat in lformat:
                    coord = [y, x + iformat[_FORMAT_BEGIN], iformat[_FORMAT_END] - iformat[_FORMAT_BEGIN]]
                    tformat = iformat[_FORMAT_FORMAT]
                    self.__process_line_format(canvas_format, coord, tformat, method = _PFORMAT_SET)
        return canvas_format

    def __form_text(self, canvas_context, canvas_format):
        canvas_display = [' ' * self.__struct[_COORD_X] for y in range(self.__struct[_COORD_Y])]
        for y, iformat in enumerate(canvas_format):
            reverse_format = iformat[:]
            reverse_format.reverse()
            context = canvas_context[y]
            for iform in reverse_format:
                context = '{pre_text}\033[{format}m{format_text}\033[0m{after_text}'.format(
                        pre_text = context[:iform[_FORMAT_BEGIN]],
                        format = iform[_FORMAT_FORMAT],
                        format_text = context[iform[_FORMAT_BEGIN] : iform[_FORMAT_END]],
                        after_text = context[iform[_FORMAT_END]:])
            canvas_display[y] = context
        return canvas_display

# debug test
if __name__ == '__main__':
    canvas = CANVAS([10, 20])
    canvas.paint('a\n' * 20)
    canvas.paint('a\n' * 20)
    canvas.paint('a\n' * 20)
    canvas.paint('a\n' * 20)
    canvas.paint('a\n' * 20)
    canvas.paint('a\n' * 20)
    canvas.paint('a\n' * 20)
    canvas.paint('a\n' * 20)
    canvas.paint('a\n' * 20)
    canvas.paint('a\n' * 20)
    canvas.sub_canvas([0, 10], [5, 5], name = 'cissy')
    canvas.dump(name = 'cissy', back = WHITE)
    # canvas.paint('hello world\n', name = 'cissy', front = BLUE)
    # canvas.dump(name = 'cissy', back = WHITE)
    # canvas.paint('i want you hello world\n', back = BLUE)
    # canvas.paint('i want you hello world\n', coordinate = [0, 4], other = TWINKLE)
    # canvas.paint('i want you hello world\n', other = INVERSE)
    # canvas.insert_format([0, 4, 5], front = PURPLE)
    # canvas.delete_format([0, 4, 5], back = PURPLE)
    # canvas.delete_format([0, 4, 5], back = BLUE)
    # canvas.set_format([0, 0, 20], front = YELLOW)
    # # canvas.paint('i want you hello world\n', coordinate = [0, 2])
    # # canvas.paint('i')
    # # canvas.paint(' want')
    # # canvas.erase()
    # # canvas.clear_area()
    # text1 = '我是你你'
    # text2 = '我你'
    # test_str1 = '|{:>12}|'.format(text1)
    # test_str2 = '|{:>12}|'.format(text2)
    # # canvas.paint(test_str1)
    # # canvas.paint(test_str2)
    # canvas.sub_canvas([0, 2], [1, 40], name = 'billy')
    # # canvas.insert_format([0, 0, 12], back = WHITE, name = 'cllen')
    # # canvas.paint(test_str1, name = 'cllen')
    # # canvas.insert_format([0, 0, 12], front = RED, name = 'billy')
    # canvas.paint(test_str2, name = 'billy')
    # # canvas.insert_format([0, 0, 4], back = WHITE, name = 'billy')
    # # canvas.insert_format([1, 1, 0], front = RED)
    # # canvas.insert_format([1, 1, 0], other = INVERSE)
    # # canvas.delete_format([1, 1, 4], other = INVERSE)
    # # canvas.insert_format([1, 1, 2], front = BLUE)
    # # canvas.insert_format([0, 1, 2], back = RED)
    # # canvas.insert_format([1, 1, 2], back = RED)
    # # canvas.insert_format([0, 1, 20], BLUE)
    # # canvas.new_area([[1, 4, 4], [0, 5, 7]], name = 'cissy')
    # # canvas.paint('dfegd', BACKSPACE, name = 'cissy', color = RED)
    # # canvas.paint('boobb', BACKSPACE, name = 'cissy', coordinate = [4, 2], color = BLUE)
    # # canvas.paint('fejke', BACKSPACE, name = 'cissy', coordinate = [4, 1], color = GREEN)
    # # canvas.new_area([[3, 3, 3], [1, 2, 2], [0, 4, 4]], name = 'cissy2')
    # # canvas.new_area([[15, 3, 3], [0, 4, 4], [0, 4, 4]], name = 'cissy3')
    canvas.display()
