#!/usr/bin/env python
# coding=utf-8

# function
#   mean
#   c

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

# choose i unit from candidate, choose permutation
# c a↓ b↑ a: len(candidate) b: b
def c(candidate, b):
    if b == 1:
        return [[x] for x in candidate]
    output = []
    for i in range(len(candidate)):
        tmps = c(candidate[i + 1 :], b - 1)
        for tmp in tmps:
            output.append([candidate[i]] + tmp)
    return output

class TopNQ(object):
    '''
    public:
      insert
      list
    private:
      __full
    '''

    def __init__(self, n):
        self.__capacity = n
        self.__list = []
        self.__score = []

    def insert(self, x, s):
        for i in range(len(self.__list)):
            if self.__score[i] < s:
                self.__score.insert(i, s)
                self.__list.insert(i, x)
                if self.__full():
                    self.__list.pop()
                    self.__score.pop()
                break
        else:
            if self.__full():
                return
            self.__list.append(x)
            self.__score.append(s)

    def list(self):
        return self.__list[:]

    def __full(self):
        return len(self.__list) >= self.__capacity
