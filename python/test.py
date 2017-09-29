#!/usr/bin/env python
# coding=utf-8
import re
import copy
import signal
import sys
import tools
import select
from datetime import datetime, timedelta

a = {1:12, 2:13}
b = {3:122, 4:133}
c = {4:a, 5:b}

if 1 in a:
    print 'a'
if 12 in a:
    print 'b'
