#!/usr/bin/env python
# coding=utf-8
'''
Magtroid @ 2019-02-11 18:06
'''

import mio
import random
import sys
import tools

_LOOP_TIMES = 1000000

def peak_game(total_player, your_position):
    left_player = total_player
    player_list = [i + 1 for i in range(total_player)]
    peak_list = []
    while left_player:
        peak_list.append(player_list.pop(int(random.random() * left_player)))
        left_player -= 1
    while len(peak_list) > 1:
        # print(peak_list)
        if your_position in peak_list:
            result = len(peak_list)
        winner_list = []
        for i in range(0, len(peak_list), 2):
            winner_list.append(min(peak_list[i], peak_list[i + 1]))
        peak_list = winner_list
    # print(peak_list)
    return result

def main(argv):
    # input all players
    print('input player number')
    total_player = int(mio.stdin())
    # input your position
    print('input your position')
    your_position = int(mio.stdin())

    distribution = dict()
    for i in range(_LOOP_TIMES):
        tools.schedule(i + 1, _LOOP_TIMES)
        ranking = peak_game(total_player, your_position)
        if ranking not in distribution:
            distribution[ranking] = 1
        else:
            distribution[ranking] += 1
    print()
    for item in sorted(distribution.items(), key = lambda d:d[1], reverse=True):
        print('{:8d} {:8d} {:16.2f}%'.format(item[0], item[1], float(item[1]) / _LOOP_TIMES * 100))

if __name__ == '__main__':
    main(sys.argv)
