#!/usr/bin/env python
# coding=utf-8

# function
#   mean

# return mean of a list
def mean(target):
    mean = 0.0
    if isinstance(target, list):
        n = 0
        for seg in target:
            if isinstance(seg, (int, float)):
                mean += seg
                n += 1
        mean /= n
    return mean
