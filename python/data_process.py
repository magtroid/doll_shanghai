#!/usr/bin/env python
# coding=utf-8
# Magtroid @ 2017-05-04 17:33
# data process

import sys
import lianjia
import proxypool
import stock
import stock_market
import log

sys.path.append('./gflags')
import gflags

FLAGS = gflags.FLAGS
gflags.DEFINE_string('target', 'stock', 'lianjia | proxy | stock_market | stock')
gflags.DEFINE_string('city', '', 'bj | sz | gz | hz | nj | cs | wh')
gflags.DEFINE_string('stock_id', '', '')
gflags.DEFINE_string('v', '0', 'vlog')

def main(argv):
    try:
        argv = FLAGS(argv) # parse flags
    except gflags.FlagsError, e:
        log.INFO('{}\nUsage: {} ARGVS\n{}'.format(e, sys.argv[0], FLAGS))
    log.set_log_level(int(FLAGS.v))

    if FLAGS.target == 'lianjia':
        if not FLAGS.city:
            log.VLOG('choose a city')
            return
        lianjia_data = lianjia.LianJiaData(FLAGS.city)
        lianjia_data.display_data()
    elif FLAGS.target == 'proxy':
        proxy_data = proxypool.ProxyPoolData()
        proxy_data.display_data()
    elif FLAGS.target == 'stock_market':
        stock_market_data = stock_market.StockMarketData()
        # stock_market_data.process_market_data()  # TODO
        stock_market_data.get_ad_ratios()
    elif FLAGS.target == 'stock':
        if not FLAGS.stock_id:
            log.VLOG('choose a stock')
            return 
        stock_data = stock.StockData(FLAGS.stock_id)
        # stock_data.display_data()  # TODO
        log.INFO(stock_data.get_ad_ratio('2017.07.07'))
    else:
        log.VLOG(FLAGS.target)
        log.VLOG('error')
    log.VLOG('done data process')

if __name__ == '__main__':
    main(sys.argv)
