#!/usr/bin/env python
# coding=utf-8
'''
Magtroid @ 2018-12-27 17:03
'''

import sys

_BUSINESS_RATIO = 0.0539
_ACCUMULATION_RATIO = 0.0325

# equal func: xn = a(bn+1 - 1) / bn(b - 1)
# xn is loan remain in last n month
# a is return loan every month, b is (1 + ratio)
# so a = xn * bn(b - 1) / (bn+1 - 1)
# e.g. 50w loan, 25year is x300 = 50

def calculate_equal(money, ratio, year):
    ratio_month = ratio / 12
    month = year * 12
    return money * (ratio_month + 1) ** month * ratio_month / ((ratio_month + 1) ** month - 1)

def calculate_principal(money, ratio, year):
    month_principal = money / year / 12
    month_interest = money * ratio / 12
    month_interest_inc = month_principal * ratio / 12
    return month_principal + month_interest, month_interest_inc

# equal every month
def calculate_equal_comb(business, accumulation, year):
    business_equal = calculate_equal(business, _BUSINESS_RATIO, year)
    accumulation_equal = calculate_equal(accumulation, _ACCUMULATION_RATIO, year)
    return business_equal, accumulation_equal

# equal principal every month
def calculate_principal_comb(business, accumulation, year):
    business_principal, business_inc = calculate_principal(business, _BUSINESS_RATIO, year)
    accumulation_principal, accumulation_inc = calculate_principal(accumulation, _ACCUMULATION_RATIO, year)
    return business_principal, accumulation_principal, business_inc, accumulation_inc

def main(argv):
    # input loan
    print('input total loan number')
    total_loan = float(sys.stdin.readline().strip()) * 10000
    print('input accumulation fund')
    accumulation = float(sys.stdin.readline().strip()) * 10000
    business = total_loan - accumulation
    print('input years')
    year = int(sys.stdin.readline().strip())
    print('')

    business_equal, accumulation_equal = calculate_equal_comb(business, accumulation, year)
    print('equal:')
    print('{:.2f} ({:.2f}+{:.2f})'.format((business_equal + accumulation_equal), business_equal, accumulation_equal))
    print('')

    business_principal, accumulation_principal, business_inc, accumulation_inc = calculate_principal_comb(business, accumulation, year)
    print('principal:')
    print('{:.2f} ({:.2f}+{:.2f})'.format((business_principal + accumulation_principal), business_principal, accumulation_principal))
    print('{:.2f} ({:.2f}+{:.2f})'.format((business_inc + accumulation_inc), business_inc, accumulation_inc))

if __name__ == '__main__':
    main(sys.argv)
