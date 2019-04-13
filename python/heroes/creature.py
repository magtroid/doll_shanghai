#!/usr/bin/env python
# coding=utf-8
'''
creature class
Magtroid @ 2019-04-12 10:54
'''

import os
import sys
sys.path.append('{}/..'.format(os.path.dirname(os.path.realpath(__file__))))
import common
import copy
import datalib
import item_creator
import log
import mio

_CREATURE_KEY = 'creature'

# hero properties
_HITPOINTS_KEY = 'hitpoints'
_ATTACK_KEY = 'attack'
_DEFENCE_KEY = 'defence'
_SPELLPOWER_KEY = 'spellpower'

class Creature(object):
    '''
    public:
      set_equipment_attack
      set_equipment_defence
      set_equipment_hitpoints
      get_name
      display_creature
    private:
    '''

    def __init__(self, name, creature_data = None):
        if creature_data is None:
            creature_lib = item_creator.ItemCreator(_CREATURE_KEY, schedule = False)
            creature_data = creature_lib.get_item(name)
        self.__name = name
        self.__hitpoints = creature_data[_HITPOINTS_KEY]
        self.__attack = creature_data[_ATTACK_KEY]
        self.__defence = creature_data[_DEFENCE_KEY]
        self.__spellpower = creature_data[_SPELLPOWER_KEY]
        self.__morale = 0
        self.__luck = 0
        self.__equipment_attack = 0
        self.__equipment_defence = 0
        self.__equipment_hitpoints = 0

    def set_equipment_attack(self, eq_attack):
        self.__equipment_attack = eq_attack

    def set_equipment_defence(self, eq_defence):
        self.__equipment_defence = eq_defence

    def set_equipment_hitpoints(self, eq_hitpoints):
        self.__equipment_hitpoints = eq_hitpoints

    def get_name(self):
        return self.__name

    def display_creature(self):
        log.VLOG('creature name: {}'.format(self.__name))
        log.VLOG('hitpoints:  {:6d}{:8s}'.format(self.__hitpoints,
                                                 '({})'.format(self.__hitpoints + self.__equipment_hitpoints)))
        log.VLOG('attack:     {:6d}{:8s}  defence:   {:6d}{:8s}'.format(
            self.__attack, '({})'.format(self.__attack + self.__equipment_attack),
            self.__defence, '({})'.format(self.__defence + self.__equipment_defence)))
        log.VLOG('spellpower: {:6d}'.format(self.__spellpower))
        log.VLOG('morale:     {:6d}          luck:      {:6d}'.format(self.__morale, self.__luck))

class CreatureCage(object):
    '''
    public:
      list_creatures
      get_creature
    private:
      __init_creatures
    '''

    def __init__(self):
        self.__creature_lib = item_creator.ItemCreator(_CREATURE_KEY)
        self.__creatures = dict()
        self.__init_creatures()

    def list_creatures(self):
        return list(self.__creatures.keys())

    def get_creature(self, creature):
        if creature not in self.__creatures.keys():
            log.VLOG('creature: {} not exist'.format(creature))
            return dict()
        return copy.deepcopy(self.__creatures[creature])

    def __init_creatures(self):
        creature_list = self.__creature_lib.item_list()
        for creature in creature_list:
            creature_data = self.__creature_lib.get_item(creature)
            self.__creatures[creature] = Creature(creature, creature_data = creature_data)

def main():
    creature_lib = item_creator.ItemCreator(_CREATURE_KEY)
    creature_name = mio.choose_command(creature_lib.item_list())
    if creature_name in common.CMD_QUIT:
        return
    creature = Creature(creature_name)
    creature.display_creature()

if __name__ == '__main__':
    main()
