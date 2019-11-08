#!/usr/bin/env python
# coding=utf-8
'''
Magtroid @ 2019-10-25 17:39
methods for chess list
'''

import auto_chess_config
import common
import datalib
import log
import tools

_NAME_KEY = 'name'

class AutoChessList(object):
    '''
    public:
      create_chess
      list_chesses
    private:
      __write_data_lib
    '''

    def __init__(self):
        self.__chess_list_path = tools.join_path([auto_chess_config.DATALIB, 'auto_chess_list.lib'])
        self.__disable_controler = True
        self.__chess_list_data_lib = datalib.DataLib(self.__chess_list_path, self.__disable_controler)
        self.__chess_list_data_lib.load_data_lib()

    def create_chess(self, name):
        new_chess = dict()
        new_chess[_NAME_KEY] = name
        self.__chess_list_data_lib.insert_data(common.EMPTY_KEY, new_chess, _NAME_KEY)
        self.__write_data_lib()

    def list_chesses(self):
        return list(self.__chess_list_data_lib.get_data())

    def __write_data_lib(self):
        self.__chess_list_data_lib.write_data_lib()

if __name__ == '__main__':
    auto_chess_list = AutoChessList()
    auto_chess_list.display()
