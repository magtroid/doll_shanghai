#!/usr/bin/env python
# coding=utf-8
'''tools for lib data store

Magtroid @ 2017-11-21 15:51
'''

# import library
import common
import datalib
import log
import os
import sys
_DETAIL_MODULE = False

def diff_lib(datalib1, datalib2):
    if type(datalib1) != type(datalib2):
        print 'type differ'
        return False
    for key in datalib1.keys():
        if key not in datalib2.keys():
            print '{} not in datalib2'.format(key)
            return False
        elif isinstance(datalib1[key], dict):
            if diff_lib(datalib1[key], datalib2[key]) == False:
                print 'diff in dict {}'.format(key)
                return False
        elif isinstance(datalib1[key], (int, float, str)):
            if datalib1[key] != datalib2[key]:
                print 'diff in value {}'.format(key)
                return False
    for key in datalib2.keys():
        if key not in datalib1.keys():
            print '{} not in datalib1'.format(key)
            return False
        elif isinstance(datalib2[key], dict):
            if diff_lib(datalib2[key], datalib1[key]) == False:
                print 'diff in dict {}'.format(key)
                return False
        elif isinstance(datalib2[key], (int, float, str)):
            if datalib2[key] != datalib1[key]:
                print 'diff in value {}'.format(key)
                return False
    return True

def file_cmp(data_file1, data_file2):
    data_lib1 = datalib.DataLib(data_file1, True)
    data_lib1.load_data_lib()
    data_lib2 = datalib.DataLib(data_file2, True)
    data_lib2.load_data_lib()
    if _DETAIL_MODULE:
        result = diff_lib(data_lib1.get_data(), data_lib2.get_data())
    else:
        result = True if data_lib1.get_data() == data_lib2.get_data() else False
    log.INFO('datalib differ') if not result else log.INFO('datalib same')

def main(argv):
    if len(argv) != 3:
        log.INFO('usage: python {} datalib1 datalib2'.format(argv[0]))
        return
    data_file1 = argv[1]
    data_file2 = argv[2]
    if os.path.isfile(data_file1) and os.path.isfile(data_file2):
        file_cmp(data_file1, data_file2)
    elif os.path.isdir(data_file1) and os.path.isdir(data_file2):
        files = os.listdir(data_file1)
        for file in files:
            file1 = '{}/{}'.format(data_file1, file)
            file2 = '{}/{}'.format(data_file2, file)
            if os.path.isfile(file1) and os.path.isfile(file2):
                file_cmp(file1, file2)
            else:
                print 'file_error'

if __name__ == common.MAIN:
    main(sys.argv)
    log.INFO('done')
