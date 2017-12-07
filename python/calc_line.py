#!/usr/bin/env python
# coding=utf-8

import os
import re
import sys

if len(sys.argv) == 1:
    t_dirs = '.'
else:
    t_dirs = sys.argv[1:]
length = 0
leng_dict = dict()
for t_dir in t_dirs:
    for filei in os.listdir(t_dir):
        if re.search('\.py$', filei):
            ffilei = '{}/{}'.format(t_dir, filei)
            with open(ffilei) as fp:
                leng = len(fp.readlines())
                leng_dict[ffilei] = leng
                length += leng

for ifile in sorted(leng_dict.items(), key = lambda d:d[1], reverse=True):
    print('{:90s}: {:4}'.format(ifile[0], ifile[1]))
print('total line number is: %d' % length)
