#!/usr/bin/env python
# coding=utf-8

import argparse
import os
import re
import sys

_EXCEPTIONS = []

class LengDict(object):
    def __init__(self, path):
        self.path = path
        self.total = 0
        self.nexts = dict()
        self.file_dict = dict()

def count_dir(t_dir):
    leng_dict = LengDict(t_dir)
    for filei in os.listdir(t_dir):
        if filei in _EXCEPTIONS:
            continue
        fullpath = os.path.join(t_dir, filei)
        length_tmp = 0
        length_dict_tmp = dict()
        if os.path.isdir(fullpath):
            leng_dict_tmp = count_dir(fullpath)
            if leng_dict_tmp.total is 0:
                continue
            leng_dict.total += leng_dict_tmp.total
            leng_dict.nexts[filei] = leng_dict_tmp
        elif re.search('\.py$', filei):
            with open(fullpath) as fp:
                lines = fp.readlines()
            length_tmp = len(lines)
            leng_dict.total += length_tmp
            leng_dict.file_dict[filei] = length_tmp
    return leng_dict

def display(leng_dict, level, clevel = 0):
    if leng_dict.nexts:
        for next in leng_dict.nexts.values():
            print('{:90s}: {:4}'.format('    ' * clevel + next.path, next.total))
            if level > 0:
                display(next, level - 1, clevel + 1)
    for ifile in sorted(leng_dict.file_dict.items(), key = lambda d:d[1], reverse=True):
        print('{:90s}: {:4}'.format('    ' * clevel + ifile[0], ifile[1]))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--indir', default = '.', help = 'check directory')
    parser.add_argument('--v', default = '0', help = 'detail level')
    args = parser.parse_args()

    leng_dict = count_dir(args.indir)
    display(leng_dict, int(args.v))
    print('total line number is: {}'.format(leng_dict.total))

if __name__ == "__main__":
    main()
