#!/usr/bin/env python
# coding=utf-8
# Magtroid @ 2017-05-04 17:33
# data process

import sys
import lianjia
import proxypool
import stock
import log

sys.path.append('./gflags')
import gflags

FLAGS = gflags.FLAGS
gflags.DEFINE_string('target', 'stock', 'lianjia | proxy | stock')
gflags.DEFINE_string('city', '', 'bj | sz | gz | hz | nj | cs | wh')
gflags.DEFINE_string('stock_id', '', '')
gflags.DEFINE_string('v', '0', 'vlog')

def main(argv):
    try:
        argv = FLAGS(argv) # parse flags
    except gflags.FlagsError, e:
        print '%s\nUsage: %s ARGVS\n%s' % (e, sys.argv[0], FLAGS)
    vlog = log.VLOG(int(FLAGS.v))

    if FLAGS.target == 'lianjia':
        if not FLAGS.city:
            vlog.VLOG('choose a city')
            return
        lianjia_data = lianjia.LianJiaData(FLAGS.city)
        lianjia_data.display_data()
    elif FLAGS.target == 'proxy':
        proxy_data = proxypool.ProxyPoolData()
        proxy_data.display_data()
    elif FLAGS.target == 'stock':
        if not FLAGS.stock_id:
            vlog.VLOG('choose a stock')
            return 
        stock_data = stock.StockData(FLAGS.stock_id)
        stock_data.display_data()
    else:
        vlog.VLOG(FLAGS.target)
        vlog.VLOG('error')
    vlog.VLOG('done data process')

if __name__ == '__main__':
    main(sys.argv)
