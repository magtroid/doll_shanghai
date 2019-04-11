#!/usr/bin/env python
# coding=utf-8
'''Class for lib data store

Magtroid @ 2017-06-27 15:51
methods for datas
'''

# import library
import canvas
import copy
import controler
import mio
import os
import re
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

    # private:
    #   __merge_data_lib
    #   __reset data_lib
    #   __write_link_data
    #   __write_data

    # resource has two types:
    #   1) string: stock id
    #   2) dict:   stock lib
    def __init__(self, resource, disable_controler = None):
        self.__root_key = [DATA_KEY, CONFIG_KEY]
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
    def load_data_lib(self, data_file = None, schedule = True):
        controler_switch = self.__disable_controler
        self.__disable_controler = True
        self_load = False
        if not data_file:
            data_file = self.__data_file
            self_load = True
        log.VLOG('start to load datalib: {}'.format(data_file))
        data_lib = dict()
        self.__reset_data_lib(data_lib)
        if os.path.exists(data_file):
            log.VLOG('Loading......')
            with open(data_file) as fp_in:
                lines = fp_in.readlines()
                i = 0
                data_file_len = len(lines) // 3
                for i in range(0, data_file_len):
                    if schedule:
                        tools.schedule(i + 1, data_file_len)
                    index = lines[i * 3]
                    keys = lines[i * 3 + 1]
                    values = lines[i * 3 + 2]

                    index_segs = index.strip().split(LIB_CONNECT)
                    # format [0] is empty
                    if index_segs[1] == 'dict':
                        unit = dict()
                    else:
                        log.VLOG('error format {}\nfail to load data lib'.format(index_segs[1]))
                        self.__reset_data_lib(data_lib)
                        self.__disable_controler = controler_switch
                        return
                    keys_segs = keys.strip().split('\t')
                    values_segs = values.strip().split('\t')
                    # process empty data
                    if index_segs[-1] == DATA_KEY and len(keys_segs) == 1 and keys_segs[0] == '':
                        keys_segs = []
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
                            # unit[keys_segs[j]] = list(map(int, data_value[1: -1].split(','))) # TODO
                            unit[keys_segs[j]] = eval(data_value) # TODO
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
            log.VLOG('no data current')
        self.set_data(CONFIG_KEY + LIB_CONNECT + _LIB_FILE_KEY, \
                        data_file, data_lib)
        log.VLOG('load ok')
        log.VLOG('all data number: {}'.format(self.data_num(data_lib)))

        if self_load:
            self.__reset_data_lib()
            self.__data_lib = data_lib
            self.__disable_controler = controler_switch
        else:
            self.__disable_controler = controler_switch
            return data_lib

    # load file data and merge into self.__data_lib
    def update_data_lib(self, file):
        prev_data = copy.deepcopy(self.__data_lib)
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
                log.VLOG('failed to insert data, no id features: {}'.format(id_feature))
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
                cdata[data_key] = copy.deepcopy(data)
                cdata[data_key][DATA_FEATURE] = data_key  # insert ID key
            else:
                cdata[data_key] = data
            self.increase_data(CONFIG_KEY + LIB_CONNECT + _DATA_NUM_KEY)
            return True
        else:
            log.VLOG('error to insert data: exists in id: {}'.format(data_key), 1)
            return False

    # delete data
    def delete_data(self, lkey):
        key_segs = lkey.split(LIB_CONNECT)
        cdata = self.get_data()
        for i in range(len(key_segs)-1):
            if key_segs[i] not in cdata:
                log.VLOG('no {} key to delete'.format(key_segs[i]))
                return False
            cdata = cdata[key_segs[i]]
        if key_segs[-1] not in cdata:
            log.VLOG('no such data: {}'.format(key_segs[-1]))
            return False
        else:
            del cdata[key_segs[-1]]
            self.decrease_data(CONFIG_KEY + LIB_CONNECT + _DATA_NUM_KEY)

            # check if parent dict is empty after delete
            # if so, delete it
            # recursive check parent dict
            for i in range(len(key_segs)-2, -1, -1):
                cdata = self.get_data()
                for j in range(i):
                    cdata = cdata[key_segs[j]]
                if len(cdata[key_segs[i]]) is 0:
                    del cdata[key_segs[i]]
            log.VLOG('success delete data: {}'.format(lkey))
            return True

    # insert config
    def insert_config(self, lkey, config, id_feature):
        if id_feature not in config:
            log.VLOG('failed to insert config, no id features: {}'.format(id_feature))
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
            cconfig[key] = copy.deepcopy(config)
            return True
        else:
            log.VLOG('error to insert config: exists in id: {}'.format(key))
            return False

    # get DATA in data lib
    # lkey represent lib path key
    # data_lib is target data lib
    def get_data(self, lkey = None, data_lib = None):
        if lkey is None:
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
                log.VLOG(key)
                log.VLOG('no such data {}'.format(lkey))
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
        log.VLOG('start to write data {}...'.format(data_file))
        if not isinstance(data_lib, dict):
            log.VLOG('error data lib type')
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

# const define
_COMMAND_MODEL = '__command__'
_FILTER_MODEL  = '__filter__'

# datalib manager
class DataLibManager(object):
    # public
    #   manage  # main function
    # private
    #   __init_lib_list
    #   __list_libs
    #   __update_skip_off
    #   __update_filter_dict
    #   __level_display
    #   __display_lib_tree

    def __init__(self):
        self.__datalib_dir = './datalib/'
        self.__disable_controler = True
        self.__target_lib = dict()
        self.__lib_list = []
        self.__init_lib_list()
        self.__canvas = canvas.CANVAS()

    # process data library
    def manage(self):
        # log.VLOG('please choose libs')
        command = mio.choose_command(self.__lib_list)
        if command == 'cancel' or command == 'q':
            log.VLOG('\ncanceled...')
        else:
            self.__target_lib = DataLib('{0}{1}'.format(self.__datalib_dir, command), self.__disable_controler)
            self.__target_lib.load_data_lib()
            self.__display_lib_tree()

    # get all libs in target dir
    def __init_lib_list(self, target_dir = None):
        if target_dir is None:
            target_dir = self.__datalib_dir
        for filen in os.listdir(target_dir):
            if re.search('\.lib$', filen):
                self.__lib_list.append(filen)

    # list all libs
    def __list_libs(self):
        tools.print_list(self.__lib_list)

    def __update_skip_off(self, offs_path, skip_off):
        head_len = 3
        sum_off = sum(offs_path) + len(offs_path) + 1
        terminal_h = tools.get_terminal_size()[0]
        while sum_off > skip_off + terminal_h - head_len:
            skip_off += 1
        while sum_off < skip_off + head_len:
            skip_off -= 1
        return skip_off

    def __update_filter_dict(self, filter_dict, filter_str):
        update_dict = dict()
        for key in filter_dict.keys():
            if re.search('^{}'.format(filter_str), key):
                update_dict[key] = filter_dict[key]
        return update_dict

    def __level_display(self, skip_offset = 0, target_lib = None, lkey_path = None, offs_path = None, level = None, filter_dict = None):
        origin_skip = skip_offset
        stair_len = 4
        if target_lib is None:
            target_lib = self.__target_lib
        if lkey_path is None:
            lkey_path = []
        if offs_path is None:
            offs_path = [0]
        if level is None:
            level = []
        n = 0
        off = 0
        filter_num = 0
        cur_node = target_lib.get_data('')
        terminal_h = tools.get_terminal_size()[0]
        if skip_offset > 0:
            skip_offset -= 1
        else:
            self.__canvas.paint('│')
        while True:
            is_tail = True if off == len(cur_node) - 1 else False
            cur_key = list(cur_node)[off]
            filtered = False
            if n == len(offs_path) - 1 and filter_dict is not None and cur_key not in filter_dict:
                filter_num += 1
                filtered = True
            if skip_offset > 0:
                skip_offset -= 1
            else:
                if not filtered:
                    stair = tools.get_stair_format(level, is_tail, stair_len)
                    cur_str = '{0}{1}'.format(stair, cur_key)
                    if not isinstance(cur_node[cur_key], dict):
                        cur_str = '{0}: {1}'.format(cur_str, cur_node[cur_key])
                    if n == len(offs_path) - 1 and off - filter_num == offs_path[n]:
                        cur_str = '{}  <--'.format(cur_str)
                    self.__canvas.paint(cur_str)
            if self.__canvas.coordinate()[0] > terminal_h - 2:
                break
            if n < len(offs_path) - 1 and off == offs_path[n] and isinstance(cur_node[cur_key], dict):
                cur_node = cur_node[cur_key]
                n += 1
                off = 0
                if is_tail:
                    level.append(0)
                else:
                    level.append(1)
            else:
                off += 1
                while len(list(cur_node)) <= off:
                    if n == 0:
                        break
                    else:
                        n -= 1
                        level.pop()
                        cur_node = target_lib.get_data(form_lkey(lkey_path[:n]))
                        off = offs_path[n] + 1
                else:
                    continue
                break
        self.__canvas.display()

    # use command to display tree structure of lib
    def __display_lib_tree(self, target_lib = None):
        command_list = ['s', 'e', 'd', 'f', mio.UP_KEY, mio.DOWN_KEY, mio.LEFT_KEY, mio.RIGHT_KEY, mio.ENTER_KEY, 'esc']
        if target_lib is None:
            target_lib = self.__target_lib
        lkey_path = []
        offs_path = [0]
        cur_lib = target_lib.get_data(form_lkey(lkey_path))
        skip_off = 0
        self.__level_display(target_lib = target_lib)
        model = _COMMAND_MODEL
        filter_dict = None
        while True:
            if model == _COMMAND_MODEL:
                command = mio.choose_command(command_list, block = False, print_log = False)
                cur_target_key = list(cur_lib)[offs_path[-1]]
                if command == mio.UP_KEY:
                    if offs_path[-1] > 0:
                        offs_path[-1] -= 1
                elif command == mio.DOWN_KEY:
                    if offs_path[-1] < len(cur_lib) - 1:
                        offs_path[-1] += 1
                elif command == mio.RIGHT_KEY or command == mio.ENTER_KEY:
                    if isinstance(cur_lib[cur_target_key], dict) and len(cur_lib[cur_target_key]) > 0:
                        lkey_path.append(cur_target_key)
                        offs_path.append(0)
                    elif cur_target_key == LINK_FEATURE:
                        sub_lib = DataLib(cur_lib[cur_target_key], self.__disable_controler)
                        sub_lib.load_data_lib()
                        self.__display_lib_tree(sub_lib)
                elif command == mio.LEFT_KEY:
                    if len(offs_path) > 1:
                        lkey_path.pop()
                        offs_path.pop()
                elif command == 'f':
                    model = _FILTER_MODEL
                    filter_str = ''
                    filter_dict = dict()
                    for n, key in enumerate(list(cur_lib)):
                        filter_dict[key] = n
                    continue
                elif command == 'esc':
                    filter_str = ''
                    model = _COMMAND_MODEL
                elif command == 'e':
                    if not isinstance(cur_lib[cur_target_key], dict):
                        p_type = type(cur_lib[cur_target_key])
                        log.VLOG('insert new data ({})'.format(p_type))
                        new = mio.stdin()
                        try:
                            new = p_type(new)
                        except:
                            log.VLOG('error format')
                        self.__target_lib.set_data(form_lkey(lkey_path + [cur_target_key]), new)
                elif command == 'd':
                    # to avoid delete only data
                    if len(cur_lib) != 1 and len(lkey_path) > 0 and lkey_path[0] == DATA_KEY:
                        self.__target_lib.delete_data(form_lkey(lkey_path[1:] + [cur_target_key]))
                        if offs_path[-1] == len(cur_lib):  # because one has been deleted
                            offs_path[-1] -= 1
                # elif command == 'u':  # TODO
                #     break
                elif command == 's':
                    log.VLOG('save and quit? (y/n)')
                    command = mio.choose_command(['y', 'n'], print_log = False)
                    if command == 'y':
                        self.__target_lib.write_data_lib()
                        break
                    else:
                        pass
                elif command == 'q':
                    break
            elif model == _FILTER_MODEL:
                command = mio.stdin(block = False)
                cur_sort_item = sorted(filter_dict.items(), key = lambda d:d[1])
                cur_target_off = cur_sort_item[offs_path[-1]][1] if len(cur_sort_item) != 0 else None
                cur_target_key = cur_sort_item[offs_path[-1]][0] if len(cur_sort_item) != 0 else None
                if command == 'esc':
                    offs_path[-1] = 0
                    filter_str = ''
                    filter_dict = None
                    model = _COMMAND_MODEL
                elif command == mio.UP_KEY:
                    if offs_path[-1] > 0:
                        offs_path[-1] -= 1
                elif command == mio.DOWN_KEY:
                    if offs_path[-1] < len(filter_dict) - 1:
                        offs_path[-1] += 1
                elif command == mio.RIGHT_KEY or command == mio.ENTER_KEY:
                    if cur_target_key is not None and isinstance(cur_lib[cur_target_key], dict):
                        filter_str = ''
                        filter_dict = None
                        model = _COMMAND_MODEL
                        offs_path[-1] = cur_target_off
                        lkey_path.append(cur_target_key)
                        offs_path.append(0)
                    elif cur_target_key == LINK_FEATURE:
                        filter_str = ''
                        filter_dict = None
                        model = _COMMAND_MODEL
                        offs_path[-1] = cur_target_off
                        sub_lib = DataLib(cur_lib[cur_target_key], self.__disable_controler)
                        sub_lib.load_data_lib(schedule = False)
                        self.__display_lib_tree(sub_lib)
                elif command == mio.LEFT_KEY:
                    if len(offs_path) > 1:
                        filter_str = ''
                        filter_dict = None
                        model = _COMMAND_MODEL
                        lkey_path.pop()
                        offs_path.pop()
                else:
                    offs_path[-1] = 0
                    filter_str += command
                    filter_dict = self.__update_filter_dict(filter_dict, filter_str)
            skip_off = self.__update_skip_off(offs_path, skip_off)
            self.__canvas.erase()
            self.__canvas.clear_area()
            self.__level_display(skip_offset = skip_off, target_lib = target_lib, lkey_path = lkey_path, offs_path = offs_path, filter_dict = filter_dict)
            cur_lib = target_lib.get_data(form_lkey(lkey_path))

if __name__ == '__main__':
    datalib_manager = DataLibManager()
    datalib_manager.manage()
    log.INFO('done')
