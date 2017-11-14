#!/usr/bin/env python
# coding=utf-8
""" python non blocking input
"""

import sys

a = ['43', '4', '32']
b = '0' if len(a) == 0 else ';'.join(sorted(a, key=lambda d:(len(d), d))) 
print b
