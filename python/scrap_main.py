#!/usr/bin/env python
# coding=utf-8
# Magtroid @ 2017-05-04 17:33
# frame works
import os
import re
import sys
import log
import time

# login files
import lianjia
import monitor
import proxy
import proxy66
import stock
import stock_market
import tools
import zhihu

import config
import gflags

FLAGS = gflags.FLAGS
gflags.DEFINE_string('target', 'stock', 'zhihu | lianjia | proxy-xici | proxy-66ip | stock_market | stock | monitor')
# gflags.DEFINE_string('account', '15101116531', '')
# gflags.DEFINE_string('password', '1122344751', '')
gflags.DEFINE_string('account', '', '')
gflags.DEFINE_string('password', '', '')
gflags.DEFINE_string('city', '', 'bj | sz | tj | qd | gz | hz | nj | cs | wh')
gflags.DEFINE_string('stock_id', '', '')
gflags.DEFINE_string('v', '0', 'vlog')

def for_test():
    print('aa')

def main(argv):
    try:
        argv = FLAGS(argv) # parse flags
    except gflags.FlagsError as e:
        log.INFO('%s\nUsage: %s ARGVS\n%s' % (e, sys.argv[0], FLAGS))
    log.set_log_level(int(FLAGS.v))

    begin = time.time()
    if FLAGS.target == 'zhihu':
        zhihu_login = zhihu.ZhihuLogin()
        zhihu_login.login(FLAGS.account, FLAGS.password)
    elif FLAGS.target == 'lianjia':
        if not FLAGS.city:
            log.VLOG('choose a city')
            return
        lianjia_login = lianjia.LianJia(FLAGS.city)
        lianjia_login.get_lianjia_data()
    elif FLAGS.target == 'proxy-xici':
        proxy_data = proxy.Proxy()
        proxy_data.get_proxy()
    elif FLAGS.target == 'proxy-66ip':
        proxy_data = proxy66.Proxy()
        proxy_data.get_proxy()
    elif FLAGS.target == 'stock_market':
        stock_market_data = stock_market.StockMarket()
        stock_market_data.get_stock_market_data()
    elif FLAGS.target == 'stock':
        if not FLAGS.stock_id:
            log.VLOG('choose a stock')
            return 
        stock_data = stock.Stock(FLAGS.stock_id)
        stock_data.get_stock_data()
        stock_data.write_stock_data()
    elif FLAGS.target == 'monitor':
        stock_monitor = monitor.StockMonitor()
        stock_monitor.stock_monitor()
    else:
        log.VLOG(FLAGS.target)
        log.VLOG('error')

    end = time.time()
    log.INFO('use time {}'.format(end - begin))
    log.VLOG('done scrap')

def ass():
    print('11')

if __name__ == '__main__':
    main(sys.argv)
