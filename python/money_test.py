#!/usr/bin/env python
# coding=utf-8

import numpy as np
from numpy import random
import time

person = [100] * 100
round = 1
while(True):
    money_range = [0] * 8
    print 'round:%d' % round
    time.sleep(0)

    for i in range(100):
        if person[i] is 0:
            continue
        person[i] -= 1
        a = int(random.random() * 99)
        if a < i:
            person[a] += 1
        else:
            person[a+1] += 1

    for i in range(100):
        if person[i] < 50:
            money_range[0] += 1
        elif person[i] < 75:
            money_range[1] += 1
        elif person[i] < 90:
            money_range[2] += 1
        elif person[i] < 100:
            money_range[3] += 1
        elif person[i] < 110:
            money_range[4] += 1
        elif person[i] < 125:
            money_range[5] += 1
        elif person[i] < 150:
            money_range[6] += 1
        else:
            money_range[7] += 1

    print sorted(person)[:10]
    print sorted(person)[-10:]
    round += 1
