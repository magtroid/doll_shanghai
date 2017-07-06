#!/usr/bin/env python
# coding=utf-8
'''Class for lib data store

Magtroid @ 2017-06-27 15:51
methods for datas
'''

import copy
import os
import re
import time
import tools

class DataLib(object):
    def __init__(self, libfile):
        self.start_date = []
        self.end_date = []
        self.data_num = 0
        self.data_file = libfile
        self.data_backup_file = '%s_backup' % libfile
        self.data_lib = dict()

    def lhas_key(self, lkey):
        key_segs = lkey.split('__')
        cdata = self.data_lib
        for key in key_segs:
            if cdata.has_key(key):
                cdata = cdata[key]
            else:
                return False
        return True

    def update_date_duration(self, date):
        if len(self.start_date) is 0:
            self.start_date = date
        if len(self.end_date) is 0:
            self.end_date = date
        if tools.date_compare(date, self.start_date) < 0:
            self.start_date = date
        if tools.date_compare(date, self.end_date) > 0:
            self.end_date = date

    def load_data(self):
        print 'start to load datalib: %s' % self.data_file
        if os.path.exists(self.data_file):
            print 'Loading......'
            with open(self.data_file) as fp_in:
                lines = fp_in.readlines()
                i = 0
                for i in range(0, len(lines), 3):
                    index = lines[i]
                    items = lines[i+1]
                    values = lines[i+2]

                    index_segs = map(str.strip, index.split('__'))
                    if index_segs[1] == 'dict':
                        unit = dict()
                    items_segs = map(str.strip, items.split('\t'))
                    values_segs = map(str.strip, values.split('\t'))
                    for j in range(len(items_segs)):
                        if re.search('^__', values_segs[j]):
                            if re.search('^__dict', values_segs[j]):
                                unit[items_segs[j]] = dict()
                        else:
                            unit[items_segs[j]] = values_segs[j]
                    if len(index_segs) is 2:
                        self.data_lib = unit.copy()
                    else:
                        unit_tmp = self.data_lib
                        for j in range(2, len(index_segs)):
                            unit_tmp = unit_tmp[index_segs[j]]
                        unit_tmp.update(unit)
                    unit.clear()
        else:
            print 'no data current'
        print 'load ok'

    def insert_data(self, lkey, data):
        key_segs = lkey.split('__')
        cdata = self.data_lib
        for key in key_segs:
            if not cdata.has_key(key):
                cdata[key] = dict()
            cdata = cdata[key]

        if data.has_key('id'):
            key = data['id']
        else:
            key = str(self.data_num + 1)
        if not cdata.has_key(key):
            cdata[key] = data.copy()
            self.data_num += 1
        else:
            print 'error to insert data: exitst in ip: %s' % key 

    def write_data(self, data, front_id, fp_out):
        if isinstance(data, dict):
            out_str = '__dict%s\n' % front_id
            fp_out.writelines(out_str)
        items = ''
        values = ''
        for key in data.keys():
            items += key + '\t'

            data_deep = data[key]
            if isinstance(data_deep, dict):
                values += '__dict__%s\t' % key
            else:
                values += '%s\t' % data_deep

        items = items[:-1] + '\n'
        fp_out.writelines(items)
        values = values[:-1] + '\n'
        fp_out.writelines(values)

        for key in data.keys():
            front_id_deep = front_id + '__' + key
            data_deep = data[key]
            if isinstance(data_deep, dict):
                self.write_data(data_deep, front_id_deep, fp_out)
            

    def write_data_lib(self):
        os.system ('cp %s %s' % (self.data_file, self.data_backup_file))
        with open(self.data_file, 'w') as fp_out:
            front_id = ''
            self.write_data(self.data_lib, front_id, fp_out)
