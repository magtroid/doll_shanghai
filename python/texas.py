#!/usr/bin/env python
# coding=utf-8
'''
Magtroid @ 2018-12-24 15:29
'''

import copy
from functools import cmp_to_key
import random
import sys
sys.path.append('./gflags')
import gflags

FLAGS = gflags.FLAGS
gflags.DEFINE_string('games', '1000', 'game numbers')

_COLOR = ['D', 'C', 'H', 'S']
_SIGN = ['♦', '♣', '♥', '♠']
_NUMBER = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
_HAND_NUM = 2
_TABLE_NUM = 5

_ROYAL_FLUSH = 'royal_flush'
_STRAIGHT_FLUSH = 'straight_flush'
_FOUR_OF_A_KIND = 'four_of_a_kind'
_FULL_HOUSE = 'full_house'
_FLUSH = 'flush'
_STRAIGHT = 'straight'
_THREE_OF_A_KIND = 'three_of_a_kind'
_TWO_PAIR = 'two_pair'
_PAIR = 'pair'
_HIGH_CARD = 'high_card'

def PokerCmp(poker1, poker2):
    return _COLOR.index(poker1.color()) - _COLOR.index(poker2.color()) if \
poker1.number() == poker2.number() else _NUMBER.index(poker1.number()) - \
_NUMBER.index(poker2.number())

def ColorDisplay():
    color_list = []
    for i in range(len(_COLOR)):
        color_list.append('{}:{}'.format(_SIGN[i], _COLOR[i]))
    return ' '.join(color_list)

class Poker(object):
    '''
    public:
      color
      number
      display
    '''
    def __init__(self, color, number):
        self.__color = color
        self.__number = number
    
    def color(self):
        return self.__color

    def number(self):
        return self.__number

    def display(self):
        return self.color() + self.number()

class Dealer(object):
    '''
    public:
      poker_num
      deal
    '''
    def __init__(self):
        self.__pokers = []
        for color in _COLOR:
            for number in _NUMBER:
                self.__pokers.append(Poker(color, number))

    def poker_num(self):
        return len(self.__pokers)

    def deal(self, poker = None):
        if self.poker_num() == 0:
            print('no cards')
            return ''
        if poker is not None:
            color, number = poker[0], poker[1:]
            for i in range(len(self.__pokers)):
                tpoker = self.__pokers[i]
                if tpoker.color() == color and tpoker.number() == number:
                    return self.__pokers.pop(i)
            else:
              print('no cards')
              return ''
        off = int(self.poker_num() * random.random())
        return self.__pokers.pop(off)

class Pokers():
    '''
      insert
      pokers
      display
      judge_result
    '''
    def __init__(self):
        self.__pokers = []

    def insert(self, poker):
        self.__pokers.append(poker)

    def pokers(self):
        return self.__pokers[:]

    def display(self):
        return ' '.join([x.display() for x in self.__pokers])

def check_straight(pokers):
    straight_list = []
    if len(pokers) >= 5 and pokers[-1].number() == 'A':
        straight_list.append([pokers[-1]] + pokers[0 : 4])
    for i in range(len(pokers) - 4):
        straight_list.append(pokers[i : i + 5])
    for straight in reversed(straight_list):
        last_num = -1 if straight[0].number() == 'A' else _NUMBER.index(straight[0].number())
        for poker in straight[1:]:
            cur_num = _NUMBER.index(poker.number()) 
            if cur_num != last_num + 1:
                break
            else:
                last_num = cur_num
        else:
            left = []
            for poker in pokers:
                if poker not in straight:
                    left.append(poker)
            return straight, left
    else:
        return [], pokers

def check_flush(pokers):
    color_list = [[], [], [], []]
    for poker in pokers:
        color_list[_COLOR.index(poker.color())].append(poker)
    for color in color_list:
        if len(color) >= 5:
            left = []
            for poker in pokers:
                if poker not in color:
                    left.append(poker)
            return color, left
    else:
        return [], pokers

def check_royal(pokers):
    if pokers[0].number() == '10':
        return pokers, []
    return [], pokers

def check_four_of_a_kind(pokers):
    number_list = [[], [], [], [], [], [], [], [], [], [], [], [], []]
    for poker in pokers:
        number_list[_NUMBER.index(poker.number())].append(poker)
    for number in number_list:
        if len(number) == 4:
            left = []
            for poker in pokers:
                if poker not in number:
                    left.append(poker)
            return number, left
    return [], pokers


def check_three_of_a_kind(pokers):
    number_list = [[], [], [], [], [], [], [], [], [], [], [], [], []]
    for poker in pokers:
        number_list[_NUMBER.index(poker.number())].append(poker)
    for number in reversed(number_list):
        if len(number) == 3:
            left = []
            for poker in pokers:
                if poker not in number:
                    left.append(poker)
            return number, left
    return [], pokers

def check_pair(pokers):
    number_list = [[], [], [], [], [], [], [], [], [], [], [], [], []]
    for poker in pokers:
        number_list[_NUMBER.index(poker.number())].append(poker)
    for number in reversed(number_list):
        if len(number) == 2:
            left = []
            for poker in pokers:
                if poker not in number:
                    left.append(poker)
            return number, left
    return [], pokers

def check_high_card(pokers, number):
    if len(pokers) >= number:
        return pokers[-number :], pokers[:-number]
    else:
        return []

def judge_result(hand_pokers, table_pokers):
    cur_pokers = hand_pokers + table_pokers
    cur_pokers = sorted(cur_pokers, key = cmp_to_key(PokerCmp))
    flush, flush_left = check_flush(cur_pokers)
    if flush:
        straight_flush, straight_flush_left = check_straight(flush)
        if straight_flush:
            royal_flush, royal_flush_left = check_royal(straight_flush)
            if royal_flush:
                return _ROYAL_FLUSH, royal_flush
            else:
                return _STRAIGHT_FLUSH, straight_flush
        else:
            return _FLUSH, flush[-5 :]
    else:
        four_of_a_kind, four_of_a_kind_left = check_four_of_a_kind(cur_pokers)
        if four_of_a_kind:
            high_card, high_card_left = check_high_card(four_of_a_kind_left, 1)
            return _FOUR_OF_A_KIND, four_of_a_kind_left + high_card
        else:
            three_of_a_kind, three_of_a_kind_left = check_three_of_a_kind(cur_pokers)
            if three_of_a_kind:
                pair, pair_left = check_pair(three_of_a_kind_left)
                if pair:
                    return _FULL_HOUSE, three_of_a_kind + pair
                else:
                    straight, straight_left = check_straight(cur_pokers)
                    if straight:
                        return _STRAIGHT, straight
                    else:
                        high_card, high_card_left = check_high_card(three_of_a_kind_left, 2)
                        return _THREE_OF_A_KIND, three_of_a_kind + high_card
            else:
                pair, pair_left = check_pair(cur_pokers)
                if pair:
                    pair2, pair2_left = check_pair(pair_left)
                    if pair2:
                        high_card, high_card_left = check_high_card(pair2_left, 1)
                        return _TWO_PAIR, pair + pair2 + high_card
                    else:
                        high_card, high_card_left = check_high_card(pair_left, 3)
                        return _PAIR, pair + high_card
                else:
                    high_card, high_card_left = check_high_card(cur_pokers, 5)
                    return _HIGH_CARD, high_card

def game(dealer, hand, table):
    while len(hand.pokers()) < _HAND_NUM:
        hand.insert(dealer.deal())
    while len(table.pokers()) < _TABLE_NUM:
        table.insert(dealer.deal())
    card_type, pokers = judge_result(hand.pokers(), table.pokers())
    return card_type, pokers
    # print('final result: {}'.format(' '.join([x.display() for x in pokers])))

def predict(dealer, hand, table):
    print('hand: {}    table: {}'.format(hand.display(), table.display()))
    results = dict()
    games = int(FLAGS.games)
    for i in range(games):
        result, pokers = game(copy.deepcopy(dealer), copy.deepcopy(hand), copy.deepcopy(table))
        if result not in results:
            results[result] = 1
        else:
            results[result] += 1
    for item in sorted(results.items(), key = lambda d:d[1], reverse=True):
        print('{:20s} {:10d}   ({:5.2f}%)'.format(item[0], item[1], item[1] / games * 100))

def main(argv):
    try:
        argv = FLAGS(argv) # parse flags
    except gflags.FlagsError as e:
        log.INFO('%s\nUsage: %s ARGVS\n%s' % (e, sys.argv[0], FLAGS))

    dealer = Dealer()
    hand = Pokers()
    table = Pokers()
    predict(dealer, hand, table)

    # flow 1
    print('choose hand card (2 cards) {}'.format(ColorDisplay()))
    input_pokers = sys.stdin.readline().strip().split()
    for poker in input_pokers:
        hand.insert(dealer.deal(poker))
    predict(dealer, hand, table)

    # flow 2
    print('flop (3 cards) {}'.format(ColorDisplay()))
    input_pokers = sys.stdin.readline().strip().split()
    for poker in input_pokers:
        table.insert(dealer.deal(poker))
    predict(dealer, hand, table)

    # flow 3
    print('turn (1 card) {}'.format(ColorDisplay()))
    input_pokers = sys.stdin.readline().strip().split()
    for poker in input_pokers:
        table.insert(dealer.deal(poker))
    predict(dealer, hand, table)

    # flow 4
    print('river (1 card) {}'.format(ColorDisplay()))
    input_pokers = sys.stdin.readline().strip().split()
    for poker in input_pokers:
        table.insert(dealer.deal(poker))
    result, pokers = game(dealer, hand, table)
    print('{} {}'.format(result, ' '.join([x.display() for x in pokers])))

if __name__ == '__main__':
    main(sys.argv)
