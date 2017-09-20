#!/usr/bin/env python
# coding=utf-8
'''Class for lib data store

Magtroid @ 2017-06-27 15:51
methods for datas
'''

# import library
import copy
import controler
import os
import re
import signal
import sys
import time
import tools
import log

# const define

# data feature
DATA_FEATURE = 'ID'
# lib link feature
LINK_FEATURE = 'LIB_LINK'

# lib type key
LIB_CONNECT      = '__'
_LIB_TYPE_DICT   = '__dict'
_LIB_TYPE_INT    = '__int'
_LIB_TYPE_FLOAT  = '__float'
_LIB_TYPE_BOOL   = '__bool'
_LIB_TYPE_LIST   = '__list'
_LIB_TYPE_STRING = '__string'
_LIB_TYPE_OTHERS = '__others'

# root key
DATA_KEY   = 'DATA'
CONFIG_KEY = 'CONFIG'

# config key
_DATA_NUM_KEY = 'DATA_NUM'
_LIB_FILE_KEY = 'LIB_FILE'

# common function
def form_lkey(path_list):
    return LIB_CONNECT.join(path_list)

# main class
class DataLib(object):
    # public:
    #   get_controler_switch
    #   load_data_lib
    #   update_data_lib
    #   get_data_lib
    #   insert_data
    #   delete_data
    #   insert_config
    #   get_data
    #   set_data
    #   increase_data
    #   decrease_data
    #   lhas_key
    #   data_num
    #   lib_file
    #   write_data_lib
    #   display  # TODO

    # private
    #   __merge_data_lib
    #   __reset data_lib
    #   __write_link_data
    #   __write_data

    # resource has two types:
    #   1) string: stock id
    #   2) dict:   stock lib
    def __init__(self, resource, disable_controler = None, vlog = 0):
        self.__root_key = [DATA_KEY, CONFIG_KEY]
        self.__vlog = log.VLOG(vlog)
        self.__disable_controler = False
        if isinstance(resource, str):
            self.__data_file = resource
            self.__data_lib = dict()
            self.__reset_data_lib()
        elif isinstance(resource, dict):
            self.__data_lib = resource
            self.__data_file = self.lib_file()

        if not disable_controler:
            self.__controler = controler.Controler(self)

    # return controler switch
    def get_controler_switch(self):
        return self.__disable_controler

    # load data lib from data_file
    # return a lib dict
    # if data_file empty, load self data file and set to self
    def load_data_lib(self, data_file = None):
        controler_switch = self.__disable_controler
        self.__disable_controler = True
        self_load = False
        if not data_file:
            data_file = self.__data_file
            self_load = True
        self.__vlog.VLOG('start to load datalib: %s' % data_file)
        data_lib = dict()
        self.__reset_data_lib(data_lib)
        if os.path.exists(data_file):
            self.__vlog.VLOG('Loading......')
            with open(data_file) as fp_in:
                lines = fp_in.readlines()
                i = 0
                data_file_len = len(lines) / 3
                for i in range(0, data_file_len):
                    tools.schedule(i + 1, data_file_len)
                    index = lines[i * 3]
                    keys = lines[i * 3 + 1]
                    values = lines[i * 3 + 2]

                    index_segs = map(str.strip, index.split(LIB_CONNECT))
                    # format [0] is empty
                    if index_segs[1] == 'dict':
                        unit = dict()
                    else:
                        self.__vlog.VLOG('error format %s\nfail to load data lib' % index_segs[1])
                        self.__reset_data_lib(data_lib)
                        self.__disable_controler = controler_switch
                        return
                    keys_segs = map(str.strip, keys.split('\t'))
                    values_segs = map(str.strip, values.split('\t'))
                    for j in range(len(keys_segs)):
                        data_format, data_value = re.search('(^__[^_]+)(.*)', values_segs[j]).groups()  # split type and value
                        # dict has no value, normal has value split with a LIB_CONNECT
                        if data_value:
                            data_value = re.sub('^%s' % LIB_CONNECT, '', data_value)
                        # process link types  # TODO(zhengzhang): fix load link
                        # if keys_segs[j] == LINK_FEATURE:
                        #     unit[keys_segs[j]] = dict()
                        #     unit[keys_segs[j]].update(self.load_data_lib(data_value))
                        #     continue

                        if data_format == _LIB_TYPE_DICT:
                            unit[keys_segs[j]] = dict()
                        elif data_format == _LIB_TYPE_INT:
                            unit[keys_segs[j]] = int(data_value)
                        elif data_format == _LIB_TYPE_FLOAT:
                            unit[keys_segs[j]] = float(data_value)
                        elif data_format == _LIB_TYPE_BOOL:
                            unit[keys_segs[j]] = bool(data_value)
                        elif data_format == _LIB_TYPE_LIST:
                            unit[keys_segs[j]] = map(int, data_value[1: -1].split(',')) # TODO
                        elif data_format == _LIB_TYPE_STRING:
                            unit[keys_segs[j]] = data_value
                        else:  # data_format == _LIB_TYPE_OTHERS
                            unit[keys_segs[j]] = data_value
                    # is not root node
                    if len(index_segs) is not 2:
                        unit_tmp = data_lib
                        for j in range(2, len(index_segs)):
                            unit_tmp = unit_tmp[index_segs[j]]
                        unit_tmp.update(unit)
        else:
            self.__vlog.VLOG('no data current')
        self.set_data(CONFIG_KEY + LIB_CONNECT + _LIB_FILE_KEY, \
                        data_file, data_lib)
        self.__vlog.VLOG('load ok')
        self.__vlog.VLOG('all data number: %d' % self.data_num(data_lib))

        if self_load:
            self.__reset_data_lib()
            self.__data_lib = data_lib
            self.__disable_controler = controler_switch
        else:
            self.__disable_controler = controler_switch
            return data_lib

    # load file data and merge into self.__data_lib
    def update_data_lib(self, file):
        prev_data = self.__data_lib.copy()
        self.load_data_lib(file)
        self.__merge_data_lib(prev_data, self.__data_lib)
        self.__data_lib = prev_data

    # return data lib
    def get_data_lib(self):
        return self.__data_lib

    # insert data
    # id_feature is the key to set ID
    def insert_data(self, lkey, data, id_feature):
        if isinstance(data, dict):
            if id_feature not in data:
                self.__vlog.VLOG('failed to insert data, no id features: ' % id_feature)
                return False
            else:
                data_key = data[id_feature]
        else:
            data_key = id_feature
        key_segs = lkey.split(LIB_CONNECT)
        cdata = self.get_data()
        for key in key_segs:
            if not key:  # pass empty key
                continue
            if key not in cdata:
                cdata[key] = dict()
            cdata = cdata[key]

        # insert data and insert ID key
        if data_key not in cdata:
            if isinstance(data, dict):
                cdata[data_key] = data.copy()
                cdata[data_key][DATA_FEATURE] = data_key  # insert ID key
            else:
                cdata[data_key] = data
            self.increase_data(CONFIG_KEY + LIB_CONNECT + _DATA_NUM_KEY)
            return True
        else:
            self.__vlog.VLOG('error to insert data: exists in id: %s' % data_key, 1)
            return False

    # delete data
    def delete_data(self, lkey):
        key_segs = lkey.split(LIB_CONNECT)
        cdata = self.get_data()
        for i in range(len(key_segs)-1):
            if key_segs[i] not in cdata:
                self.__vlog.VLOG('no %s key to delete' % key_segs[i])
                return False
            cdata = cdata[key_segs[i]]
        if key_segs[-1] not in cdata:
            self.__vlog.VLOG('no such data: %s' % key_segs[-1])
            return False
        else:
            del cdata[key_segs[-1]]
            self.decrease_data(CONFIG_KEY + LIB_CONNECT + _DATA_NUM_KEY)

            # check if parent dict is empty after delete
            # if so, delete it
            # recursive check parent dict
            for i in range(len(key_segs)-2, -1, -1):
                cdata = self.get_data()
                for j in range(i-1):
                    cdata = cdata[key_segs[j]]
                if len(cdata[key_segs[i]]) is 0:
                    del cdata[key_segs[i]]
            self.__vlog.VLOG('success delete data: %s' % lkey)
            return True

    # insert config
    def insert_config(self, lkey, config, id_feature):
        if id_feature not in config:
            self.__vlog.VLOG('failed to insert config, no id features: ' % id_feature)
            return False
        key_segs = lkey.split(LIB_CONNECT)
        cconfig = self.get_data(CONFIG_KEY)
        for key in key_segs:
            if not key:  # pass empty key
                continue
            if key not in cconfig:
                cconfig[key] = dict()
            cconfig = cconfig[key]

        # insert config
        key = config[id_feature]
        if key not in cconfig:
            cconfig[key] = config.copy()
            return True
        else:
            self.__vlog.VLOG('error to insert config: exists in id: %s' % key)
            return False

    # get DATA in data lib
    # lkey represent lib path key
    # data_lib is target data lib
    def get_data(self, lkey = None, data_lib = None):
        if not lkey:
            lkey = DATA_KEY
        if not data_lib:
            cdata = self.__data_lib
        else:
            cdata = data_lib
        key_segs = lkey.split(LIB_CONNECT)
        for key in key_segs:
            if not key:  # pass empty key
                continue
            if isinstance(cdata, dict) and key in cdata:
                cdata = cdata[key]
            else:
                self.__vlog.VLOG(key)
                self.__vlog.VLOG('no such data %s' % lkey)
                return None
        return cdata

    # set data value, if not exist, form one
    # if data_lib exist, set data lib instead
    def set_data(self, lkey, value, data_lib = None):
        if data_lib == None:
            data_lib = self.__data_lib
        key_segs = lkey.split(LIB_CONNECT)
        cdata = data_lib
        for key in key_segs[:-1]:
            if key not in cdata:
                cdata[key] = dict()
            cdata = cdata[key]
        cdata[key_segs[-1]] = value

    # increase data value by number (default 1)
    def increase_data(self, lkey, number = None):
        if not number:
            number = 1
        if self.lhas_key(lkey):
            key_segs = lkey.split(LIB_CONNECT)
            cdata = self.__data_lib
            for key in key_segs[:-1]:
                cdata = cdata[key]
            last_key = key_segs[-1]
            if isinstance(cdata[last_key], (int, float)):
                cdata[last_key] += number

    # decrease data value by number (default 1)
    def decrease_data(self, lkey, number = None):
        if not number:
            number = 1
        if self.lhas_key(lkey):
            key_segs = lkey.split(LIB_CONNECT)
            cdata = self.__data_lib
            for key in key_segs[:-1]:
                cdata = cdata[key]
            last_key = key_segs[-1]
            if isinstance(cdata[last_key], (int, float)):
                cdata[last_key] -= number

    # check if data lib has key
    def lhas_key(self, lkey):
        key_segs = lkey.split(LIB_CONNECT)
        cdata = self.__data_lib
        for key in key_segs:
            if key in cdata:
                cdata = cdata[key]
            else:
                return False
        return True

    # return data number of data lib
    # data lib not exist, return self data number
    def data_num(self, data_lib = None):
        if data_lib:
            return self.get_data(CONFIG_KEY + LIB_CONNECT + _DATA_NUM_KEY, data_lib)
        else:
            return self.get_data(CONFIG_KEY + LIB_CONNECT + _DATA_NUM_KEY)

    # return file name of data lib
    # data lib not exist, return self file name
    def lib_file(self, data_lib = None):
        if data_lib:
            return self.get_data(CONFIG_KEY + LIB_CONNECT + _LIB_FILE_KEY, data_lib)
        else:
            return self.get_data(CONFIG_KEY + LIB_CONNECT + _LIB_FILE_KEY)


    # copy a backup and write data
    # parameter: data_lib  --> data to write (default: self.__data_lib)
    #            data_file --> target file   (default: self.__data_file)
    def write_data_lib(self, data_lib = None, data_file = None, backup = True):
        if not data_lib:
            data_lib = self.__data_lib
        if not data_file:
            data_file = self.lib_file() if self.lib_file() else self.__data_file
        self.set_data(CONFIG_KEY + LIB_CONNECT + _LIB_FILE_KEY, data_file)
        self.__vlog.VLOG('start to write data %s...' % data_file)
        if not isinstance(data_lib, dict):
            self.__vlog.VLOG('error data lib type')
            return
        if os.path.isfile(data_file) and backup == True:
            os.system ('cp %s %s' % (data_file, '%s_backup' % data_file))
        else:
            if re.search('/', data_file):
                file_dir = re.search('(.*)/', data_file).group(1)
                if not os.path.isdir(file_dir):
                    os.makedirs(file_dir)
        with open(data_file, 'w') as fp_out:
            id_prefix = ''
            self.__write_data(data_lib, id_prefix, fp_out)

    # reset data lib to default
    # if data_lib exist, reset data lib instead
    def __reset_data_lib(self, data_lib = None):
        self_reset = False
        if data_lib == None:
            self_reset = True
            data_lib = self.__data_lib
        data_lib.clear()
        for key in self.__root_key:
            data_lib[key] = dict()

        if self_reset:
            self.set_data(CONFIG_KEY + LIB_CONNECT + _DATA_NUM_KEY, 0)
            self.set_data(CONFIG_KEY + LIB_CONNECT + _LIB_FILE_KEY, '')
        else:
            self.set_data(CONFIG_KEY + LIB_CONNECT + _DATA_NUM_KEY, 0, data_lib)
            self.set_data(CONFIG_KEY + LIB_CONNECT + _LIB_FILE_KEY, '', data_lib)

    # only merge new dict in new data
    # merge data2 into data1
    def __merge_data_lib(self, data1, data2):
        for key in data2.keys():
            if isinstance(data2[key], dict):
                if key not in data1:
                    data1[key] = data2[key]
                    # check if data increase data number
                    if DATA_FEATURE in data1[key]:
                        self.increase_data(CONFIG_KEY + LIB_CONNECT + _DATA_NUM_KEY)
                else:
                    self.__merge_data_lib(data1[key], data2[key])

    # write link data lib
    def __write_link_data(self, link_data):
        link_file = self.lib_file(link_data)
        self.write_data_lib(link_data, link_file)

    # recursive write data, type is dict
    def __write_data(self, data, id_prefix, fp_out):
        out_str = _LIB_TYPE_DICT + id_prefix + '\n'
        fp_out.writelines(out_str)

        keys = ''
        values = ''
        for key in data.keys():
            keys += key + '\t'

            # write link feature key and value: file name
            if key == LINK_FEATURE:
                if isinstance(data[key], dict):
                    value = self.lib_file(data[key])
                    self.__write_link_data(data[key])
                    data[key] = value

            value = data[key]
            value_str = LIB_CONNECT + str(value)
            if isinstance(value, dict):
                values += _LIB_TYPE_DICT + '\t'
            elif isinstance(value, int):
                values += _LIB_TYPE_INT + value_str + '\t'
            elif isinstance(value, float):
                values += _LIB_TYPE_FLOAT + value_str + '\t'
            elif isinstance(value, bool):
                values += _LIB_TYPE_BOOL + value_str + '\t'
            elif isinstance(value, list):
                values += _LIB_TYPE_LIST + value_str + '\t'
            elif isinstance(value, str):
                values += _LIB_TYPE_STRING + value_str + '\t'
            else:
                values += _LIB_TYPE_OTHERS + value_str + '\t'

        keys = '%s\n' % keys.strip()
        values = '%s\n' % values.strip()
        fp_out.writelines(keys)
        fp_out.writelines(values)

        for key in data.keys():
            id_prefix_deep = id_prefix + LIB_CONNECT + key
            data_deep = data[key]
            if isinstance(data_deep, dict):
                self.__write_data(data_deep, id_prefix_deep, fp_out)
