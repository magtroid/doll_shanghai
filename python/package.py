#!/usr/bin/env python
# coding=utf-8

import mio
import log
import tools

# _HK = 0.8829
_HK = 0.8961
_MT = 15.5

def get_exchange():
    bank = '招商银行'
    currency = '港币'
    exchange_data = tools.currency_exchange_ratio(bank, currency)
    ratio = float(exchange_data['buyPrice1']) / 100
    log.INFO('hk exchange ratio: {}'.format(ratio))
    return ratio

def calc_c():
    log.INFO('input base')
    # base = float(mio.stdin().strip())
    base = 48000
    return base * _MT

def calc_s():
    log.INFO('input number')
    # s = float(mio.stdin().strip())
    s = 1750
    log.INFO('input price')
    price = float(mio.stdin().strip())
    exchange_ratio = get_exchange()
    return s * price * exchange_ratio

def main():
    c = calc_c()
    log.INFO('total: {}'.format(c + calc_s()))

if __name__ == '__main__':
    main()
