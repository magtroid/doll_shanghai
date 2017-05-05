#!/usr/bin/env python
# coding=utf-8
# Magtroid @ 2017-05-04 17:33
# frame works
import os
import re
import sys
import github
from zhihu import login
sys.path.append('./gflags')
import gflags

FLAGS = gflags.FLAGS
gflags.DEFINE_string('target_type', 'zhihu', '')
gflags.DEFINE_string('usr_id', 'magtroid', '')
gflags.DEFINE_string('password', '', '')

def main(argv):
    try:
        argv = FLAGS(argv) # parse flags
    except gflags.FlagsError, e:
        print '%s\nUsage: %s ARGVS\n%s' % (e, sys.argv[0], FLAGS)

    # login()
    github_login = github.GithubLogin()
    github_login.login(FLAGS.usr_id, FLAGS.password)

    print 'done'

if __name__ == '__main__':
    main(sys.argv)
