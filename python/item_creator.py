#!/usr/bin/env python
# coding=utf-8
# Magtroid @ 2019-01-06 19:08

import hero_config
import common
import datalib
import log
import mio

_STRUCT_KEY = '_struct'
_INSTANCE_KEY = '_instance'

_STRUCT_PROCESS_COMMAND = ['e', 'q']
_STRUCT_EDIT_COMMAND = ['a', 'd', 's', 'q']
_STRUCT_FEATURE_TYPE = [common.TYPE_STRING, common.TYPE_INT, common.TYPE_FLOAT]

_NEW_ITEM = '_new_item'
_NAME_KEY = 'name'

_ITEM_ORI_KEY = [_NAME_KEY, datalib.DATA_FEATURE]

class ItemCreator(object):
    '''
    public:
      process_item
      item_list
      get_item
    private:
      __creator_init
      __display_structure
      __process_item_structure
      __process_item_instance
      __create_new_item
      __check_structure_update
      __write_data_lib
    '''

    def __init__(self, name = None, schedule = True):
        if name is None:
            log.VLOG('input your item name')
            name = mio.stdin()
        self.__item_data_path = './datalib/' + name + '.lib'
        self.__item_data_lib = datalib.DataLib(self.__item_data_path)
        self.__item_data_lib.load_data_lib(schedule = schedule)
        self.__creator_init()

    def process_item(self):
        data = self.__item_data_lib.get_data()
        while True:
            command = mio.choose_command(list(data.keys()))
            if command == _STRUCT_KEY:
                self.__process_item_structure()
            elif command == _INSTANCE_KEY:
                self.__process_item_instance()
            elif command in common.CMD_QUIT:
                break
        save_or_not = mio.choose_command(common.YON_COMMAND)
        if save_or_not is common.Y_COMMAND:
            self.__write_data_lib()

    def item_list(self):
        instances = self.__item_data_lib.get_data(datalib.form_lkey([datalib.DATA_KEY, _INSTANCE_KEY]))
        return list(set(instances.keys()) - set(_ITEM_ORI_KEY))

    def get_item(self, key):
        instances = self.__item_data_lib.get_data(datalib.form_lkey([datalib.DATA_KEY, _INSTANCE_KEY]))
        if key in instances:
            return instances[key]
        else:
            log.VLOG('can not find item: {}'.format(key))
            return {}

    def __creator_init(self):
        data = self.__item_data_lib.get_data()
        if _STRUCT_KEY not in data:
            struct = dict()
            struct[_NAME_KEY] = _STRUCT_KEY
            self.__item_data_lib.insert_data(common.EMPTY_KEY, struct, _NAME_KEY)
        if _INSTANCE_KEY not in data:
            instance = dict()
            instance[_NAME_KEY] = _INSTANCE_KEY
            self.__item_data_lib.insert_data(common.EMPTY_KEY, instance, _NAME_KEY)

    def __display_structure(self, struct = None):
        if struct is None:
            struct = self.__item_data_lib.get_data(datalib.form_lkey([datalib.DATA_KEY, _STRUCT_KEY]))
        for key, value in struct.items():
            if key not in _ITEM_ORI_KEY:
                log.VLOG('{} --> {}'.format(key, value))

    def __process_item_structure(self):
        struct = self.__item_data_lib.get_data(datalib.form_lkey([datalib.DATA_KEY, _STRUCT_KEY]))
        self.__display_structure()
        command = mio.choose_command(_STRUCT_PROCESS_COMMAND)
        if command == 'e':
            log.VLOG('start to edit struct')
            while True:
                command_e = mio.choose_command(_STRUCT_EDIT_COMMAND)
                if command_e == 'a':
                    log.VLOG('add a new feature, please input feature name')
                    feature_name = mio.stdin()
                    if feature_name not in struct.keys():
                        log.VLOG('please input feature {}\'s type'.format(feature_name))
                        feature_type = mio.choose_command(_STRUCT_FEATURE_TYPE)
                        if feature_type in common.CMD_QUIT:
                            continue
                        struct[feature_name] = feature_type
                        self.__display_structure(struct)
                    else:
                        log.VLOG('feature {} is already used'.format(feature_name))
                elif command_e == 'd':
                    log.VLOG('delete a feature, please select which feature to delete')
                    feature_name = mio.choose_command(list(set(struct.keys()) - set(_ITEM_ORI_KEY)))
                    if feature_name in common.CMD_QUIT:
                        continue
                    del struct[feature_name]
                    self.__display_structure(struct)
                elif command_e == 's':
                    self.__item_data_lib.set_data(datalib.form_lkey([datalib.DATA_KEY, _STRUCT_KEY]), struct)
                elif command_e == 'q':
                    break
                else:
                    log.VLOG('not support this command {}'.format(command_e))

    def __process_item_instance(self):
        instances = self.__item_data_lib.get_data(datalib.form_lkey([datalib.DATA_KEY, _INSTANCE_KEY]))
        while True:
            instance = mio.choose_command(list(set(instances.keys()) - set(_ITEM_ORI_KEY)) + [_NEW_ITEM])
            if instance == _NEW_ITEM:
                log.VLOG('insert new item name')
                name = mio.stdin()
                item_data = self.__create_new_item(name)
                self.__item_data_lib.insert_data(_INSTANCE_KEY, item_data, _NAME_KEY)
            elif instance == 'q':
                break
            else:
                self.__check_structure_update(instances[instance])
                print(instances[instance])

    def __create_new_item(self, name):
        new_item = dict()
        new_item[_NAME_KEY] = name
        self.__check_structure_update(new_item)
        return new_item

    def __check_structure_update(self, instance):
        log.VLOG('check structure of {}'.format(instance[_NAME_KEY]))
        struct = self.__item_data_lib.get_data(datalib.form_lkey([datalib.DATA_KEY, _STRUCT_KEY]))
        # check structure feature all in instance
        for feature in list(set(struct.keys()) - set(_ITEM_ORI_KEY)):
            if feature not in instance.keys():
                if struct[feature] == common.TYPE_STRING:
                    instance[feature] = ''
                    log.VLOG('insert new feature: {}, type: {}'.format(feature, struct[feature]))
                    instance[feature] = str(mio.stdin())
                elif struct[feature] == common.TYPE_INT:
                    instance[feature] = 0
                    log.VLOG('insert new feature: {}, type: {}'.format(feature, struct[feature]))
                    instance[feature] = int(mio.stdin())
                elif struct[feature] == common.TYPE_FLOAT:
                    instance[feature] = 0.0
                    log.VLOG('insert new feature: {}, type: {}'.format(feature, struct[feature]))
                    instance[feature] = float(mio.stdin())
        # check instance feature all in structure
        for feature in list(set(instance.keys()) - set(_ITEM_ORI_KEY)):
            if feature not in struct.keys():
                log.VLOG('feature: {} is no in structure, delete or not'.format(feature))
                del_or_not = mio.choose_command(common.YON_COMMAND)
                if del_or_not is common.Y_COMMAND:
                    del instance[feature]
            
    def __write_data_lib(self):
        self.__item_data_lib.write_data_lib()

if __name__ == '__main__':
    item_creator = ItemCreator()
    item_creator.process_item()
