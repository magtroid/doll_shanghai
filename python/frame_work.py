#!/usr/bin/env python
# coding=utf-8
# Magtroid @ 2017-05-04 17:33
# frame works
import os
import re
import sys

# login files
import github
import zhihu
import uqer

sys.path.append('./gflags')
import gflags

FLAGS = gflags.FLAGS
gflags.DEFINE_string('target', 'zhihu', 'zhihu | github | uqer')
# gflags.DEFINE_string('account', '15101116531', '')
# gflags.DEFINE_string('password', '1122344751', '')
gflags.DEFINE_string('account', '', '')
gflags.DEFINE_string('password', '', '')

def main(argv):
    try:
        argv = FLAGS(argv) # parse flags
    except gflags.FlagsError, e:
        print '%s\nUsage: %s ARGVS\n%s' % (e, sys.argv[0], FLAGS)

    if FLAGS.target == 'zhihu':
        zhihu_login = zhihu.ZhihuLogin()
        zhihu_login.login(FLAGS.account, FLAGS.password)
    elif FLAGS.target == 'github':
        github_login = github.GithubLogin()
        github_login.login(FLAGS.account, FLAGS.password)
    elif FLAGS.target == 'uqer':
        uqer_login = uqer.UqerLogin()
        uqer_login.login(FLAGS.account, FLAGS.password)
    else:
        print FLAGS.target
        print 'error'

    print 'done'

if __name__ == '__main__':
    main(sys.argv)
