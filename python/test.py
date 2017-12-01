#!/usr/bin/env python
# coding=utf-8
""" python non blocking input
"""
import datalib
import pprint

a = datalib.DataLib('datalib/bj_lianjia.lib')
a.load_data_lib()
pprint.pprint(a._DataLib__data_lib)
