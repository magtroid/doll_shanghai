#!/usr/bin/env python
# coding=utf-8
# Magtroid @ 2017-05-04 17:33
# frame works
import os
import re
import sys

# login files
import github
import lianjia
import uqer
import proxy
import proxy66
import zhihu

sys.path.append('./gflags')
import gflags

FLAGS = gflags.FLAGS
gflags.DEFINE_string('target', 'lianjia', 'zhihu | github | uqer | lianjia | proxy-xici | proxy-66ip')
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
        uqer_login.get_param()
    elif FLAGS.target == 'lianjia':
        lianjia_login = lianjia.LianJia()
        lianjia_login.get_chengjiao()
    elif FLAGS.target == 'proxy-cixi':
        proxy_data = proxy.Proxy()
        proxy_data.get_proxy()
    elif FLAGS.target == 'proxy-66ip':
        proxy_data = proxy66.Proxy()
        proxy_data.get_proxy()
    else:
        print FLAGS.target
        print 'error'

    print 'done'

if __name__ == '__main__':
    main(sys.argv)
