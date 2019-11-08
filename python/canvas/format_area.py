#!/usr/bin/env python
# coding=utf-8
'''
class for format area
Magtroid @ 2019-05-09 17:08
'''

import canvas_config

import area
import log
from define import *

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
_EMPTY_FORMAT = '0'
_FORMAT_SEP = ';'  # format seperate sign

# format e.g. 37 46, first one stands for format type, second stands for color
_TYPE_OFFSET = 0
_COLOR_OFFSET = 1
_TYPE_OTHER = '0'
_TYPE_FRONT = '3'
_TYPE_BACK = '4'

# process format methods
_PFORMAT_SET = '__set__'
_PFORMAT_APPEND = '__append__'
_PFORMAT_DELETE = '__delete__'

# format coord [y, x, len]
_FCOORD_LEN = 2

# format format [begin, end, format]
FORMAT_BEGIN = 0
FORMAT_END = 1
FORMAT_FORMAT = 2

class FormatArea(area.Area):
    '''
    public:
      set_format
      insert_format
      delete_formaa
      erase
      get_format
      display
    private:
      __erase
      __join_form
      __process_line_format
      __unfold_format_line
      __fold_format_line
      __format_add
      __format_min
    '''

    def __init__(self, struct = None):
        super().__init__(struct = struct)
        self.__format = []
        self.__erase()

    # coord is [y, x, len]
    def set_format(self, coord, other = '', front = '', back = ''):
        if coord[COORD_Y] >= self.struct()[COORD_Y]:
            return
        joined_form = self.__join_form(other, front, back)
        if joined_form:
            self.__process_line_format(coord, joined_form, method = _PFORMAT_SET)

    # coord is [y, x, len]
    def insert_format(self, coord, other = '', front = '', back = ''):
        if coord[COORD_Y] >= self.struct()[COORD_Y]:
            return
        joined_form = self.__join_form(other, front, back)
        if joined_form:
            self.__process_line_format(coord, joined_form)

    # coord is [y, x, len]
    def delete_format(self, coord, other = '', front = '', back = ''):
        if coord[COORD_Y] >= self.struct()[COORD_Y]:
            return
        joined_form = self.__join_form(other, front, back)
        if joined_form:
            self.__process_line_format(coord, joined_form, method = _PFORMAT_DELETE)

    def erase(self):
        self.__erase()

    def get_format(self):
        return self.__format[:]

    def display(self):
        for format in self.__format:
            log.VLOG(repr(format))

    def __erase(self):
        self.__format = [[[0, self.struct()[COORD_X], _EMPTY_FORMAT]] for y in range(self.struct()[COORD_Y])]

    # join target 3 types of forms into 1 string character
    def __join_form(self, other, front, back):
        form_list = []
        if other in _FORMAT_PALLET:
            form_list.append(_FORMAT_PALLET[other])
        if front in _COLOR_PALLET:
            form_list.append('{feature_id}{color_id}'.format(feature_id = _TYPE_FRONT,
                                                             color_id = _COLOR_PALLET[front]))

        if back in _COLOR_PALLET:
            form_list.append('{feature_id}{color_id}'.format(feature_id = _TYPE_BACK,
                                                             color_id = _COLOR_PALLET[back]))
        return _FORMAT_SEP.join(form_list)

    # process self coord format to tformat
    # coord is [y, x, len]
    def __process_line_format(self, coord, tformat, method = _PFORMAT_APPEND):
        format_line = self.__unfold_format_line(coord[COORD_Y])
        if coord[COORD_X] >= len(format_line):
            return
        begin = coord[COORD_X]
        end = min(len(format_line), coord[COORD_X] + coord[_FCOORD_LEN])
        if method == _PFORMAT_APPEND:
            format_line[begin : end] = [self.__format_add(i, tformat) for i in format_line[begin : end]]
        elif method == _PFORMAT_SET:
            format_line[begin : end] = [tformat for i in range(end - begin)]
        elif method == _PFORMAT_DELETE:
            format_line[begin : end] = [self.__format_min(i, tformat) for i in format_line[begin : end]]
        else:
            return
        self.__fold_format_line(format_line, coord[COORD_Y])

    # unfold self format line y
    def __unfold_format_line(self, y):
        format_line = [_EMPTY_FORMAT for x in range(self.struct()[COORD_X])]
        for iformat in self.__format[y]:
            format_line[iformat[FORMAT_BEGIN] : iformat[FORMAT_END]] = [iformat[FORMAT_FORMAT] for i in range(iformat[FORMAT_END] - iformat[FORMAT_BEGIN])]
        return format_line

    # fold format_line to self format line y
    def __fold_format_line(self, format_line, y):
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
        self.__format[y] = result[:]

    # dict key is format type: front back and use '0' for other, value is target format
    def __format_add(self, a, b):
        type_dict = dict()
        a_list = a.split(_FORMAT_SEP)
        for iformat in a_list:
            if iformat == _EMPTY_FORMAT:
                continue
            # other format type is 0x and front is 3, back is 4
            format_type = '{}{}'.format(_OTHER, iformat[_TYPE_OFFSET]) if len(iformat) == 1 else iformat[_TYPE_OFFSET]
            type_dict[format_type] = iformat
        b_list = b.split(_FORMAT_SEP)
        for iformat in b_list:
            if iformat == _EMPTY_FORMAT:
                continue
            # other format type is 0x and front is 3, back is 4
            format_type = '{}{}'.format(_OTHER, iformat[_TYPE_OFFSET]) if len(iformat) == 1 else iformat[_TYPE_OFFSET]
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
            format_type = '{}{}'.format(_OTHER, iformat[_TYPE_OFFSET]) if len(iformat) == 1 else iformat[_TYPE_OFFSET]
            type_dict[format_type] = iformat
        b_list = a.split(_FORMAT_SEP)
        for iformat in b_list:
            if iformat == _EMPTY_FORMAT:
                continue
            # other format type is 0x and front is 3, back is 4
            format_type = '{}{}'.format(_OTHER, iformat[_TYPE_OFFSET]) if len(iformat) == 1 else iformat[_TYPE_OFFSET]
            if format_type in type_dict:
                del type_dict[format_type]
        result = _EMPTY_FORMAT if not type_dict else _FORMAT_SEP.join(sorted(type_dict.values(), key = lambda d:(len(d), d)))
        return result

if __name__ == '__main__':
    format_area = FormatArea([10, 20])
    format_area.set_format([1, 1, 10], back = BLUE)
    format_area.insert_format([2, 1, 10], back = BLUE)
    format_area.delete_format([1, 1, 5], back = BLUE)
    format_area.display()
