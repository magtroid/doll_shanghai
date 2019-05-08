#!/usr/bin/env python
# coding=utf-8

import os
import sys
import re

def form_file(filename):
    filename = re.sub(' ', '\ ', filename)
    filename = re.sub('\(', '\(', filename)
    filename = re.sub('\)', '\)', filename)
    return filename

def main(argv):
    if len(argv) != 2:
        return
    music_dir = argv[1]
    for root, dirs, files in os.walk(music_dir):
        for cfile in files:
            group = re.search('.*\((.*)\).*\.mp3', cfile)
            if group:
                old_file = os.path.join(root, cfile)
                new_file = os.path.join(root, '{}.mp3'.format(group.group(1)))
                exec_cmd = 'mv {} {}'.format(form_file(old_file), form_file(new_file))
                print(exec_cmd)
                os.popen(exec_cmd)
        

if __name__ == '__main__':
    main(sys.argv)
