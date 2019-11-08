#!/usr/bin/env python
# coding=utf-8

import os
import sys

_LOAN_RATE = 0.6

def main(argv):
    print('input total price (万)')
    total_price = float(sys.stdin.readline().strip())
    loan = int(total_price * _LOAN_RATE)
    down_payment = '{:.4f}'.format(total_price - loan)
    print('down payment: {}'.format(down_payment))
    print('total loan: {}'.format(loan))
    os.system('python loan_caculator.py {}'.format(loan))

if __name__ == '__main__':
    main(sys.argv)
