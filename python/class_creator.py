#!/usr/bin/env python
# coding=utf-8
# Magtroid @ 2019-04-04 11:12

import common
import datalib
import item_creator
import log
import mio

_NEW_CLASS = '_new_class'
_NAME_KEY = 'name'

class ClassCreator(object):
    '''
    public:
    '''

    def __init__(self):
        self.__class_data_path = './datalib/class_creator.lib'
        self.__class_data_lib = datalib.DataLib(self.__class_data_path)
        self.__class_data_lib.load_data_lib()

    def create_class(self):
        data = self.__class_data_lib.get_data()
        while True:
            command = mio.choose_command(list(data.keys()) + [_NEW_CLASS])
            if command == _NEW_CLASS:
                self.__new_class()
            elif command in common.CMD_QUIT:
                break
            else:
                icreator = item_creator.ItemCreator(command)
                icreator.process_item()
        self.__write_data_lib()

    def __new_class(self):
        log.VLOG('insert new class name')
        name = mio.stdin()
        log.VLOG('new class name is {}'.format(name))
        class_data = dict()
        class_data[_NAME_KEY] = name
        self.__class_data_lib.insert_data(common.EMPTY_KEY, class_data, _NAME_KEY)
        icreator = item_creator.ItemCreator(name)
        icreator.process_item()

    def __write_data_lib(self):
        self.__class_data_lib.write_data_lib()

if __name__ == '__main__':
    class_creator = ClassCreator()
    class_creator.create_class()
