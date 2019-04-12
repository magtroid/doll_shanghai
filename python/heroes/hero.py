#!/usr/bin/env python
# coding=utf-8
'''
hero class
Magtroid @ 2019-04-11 17:14
'''

import os
import sys
sys.path.append('{}/..'.format(os.path.dirname(os.path.realpath(__file__))))
import common
import creature
import datalib
import item_creator
import log
import mio

_HERO_KEY = 'hero'

# hero properties
_ATTACK_KEY = 'attack'
_DEFENCE_KEY = 'defence'
_SPELLPOWER_KEY = 'spellpower'
_KNOWLEDGE_KEY = 'knowledge'

# army properties
_MAX_ARMY_NUM = 7
_ARMY_NUM_KEY = 'army_num'
_ARMY_CREATURE_KEY = 'army_creature'

class Hero(object):
    '''
    public:
      create_army
      display_hero
    private:
      __equipment_army
      __equipment_one_army
      __display_army
    '''

    def __init__(self, name):
        hero_lib = item_creator.ItemCreator(_HERO_KEY, schedule = False)
        hero_data = hero_lib.get_item(name)
        self.__name = name
        self.__attack = hero_data[_ATTACK_KEY]
        self.__defence = hero_data[_DEFENCE_KEY]
        self.__spellpower = hero_data[_SPELLPOWER_KEY]
        self.__knowledge = hero_data[_KNOWLEDGE_KEY]
        self.__morale = 0
        self.__luck = 0
        self.__level = 1
        self.__army = []

    def create_army(self, creature, num):
        if not isinstance(num, int):
            log.VLOG('number: {} is illegal'.format(num))
            return
        if len(self.__army) >= _MAX_ARMY_NUM:
            log.VLOG('army full')
            return
        if num <= 0:
            log.VLOG('army number should above 0')
            return
        army = dict()
        army[_ARMY_NUM_KEY] = num
        army[_ARMY_CREATURE_KEY] = creature
        self.__equipment_one_army(army)
        self.__army.append(army)

    def display_hero(self):
        log.VLOG('hero name: {}'.format(self.__name))
        log.VLOG('attack:     {:6d}  defence:   {:6d}'.format(self.__attack, self.__defence))
        log.VLOG('spellpower: {:6d}  knowledge: {:6d}'.format(self.__spellpower, self.__knowledge))
        log.VLOG('morale:     {:6d}  luck:      {:6d}'.format(self.__morale, self.__luck))
        for army in self.__army:
            self.__display_army(army)

    # equipment all army with hero properties
    def __equipment_army(self):
        for army in self.__army:
            self.__equipment_one_army(army)

    # equipment single army with hero properties
    def __equipment_one_army(self, army):
        army[_ARMY_CREATURE_KEY].set_equipment_attack(self.__attack)
        army[_ARMY_CREATURE_KEY].set_equipment_defence(self.__defence)

    def __display_army(self, army):
        creature = army[_ARMY_CREATURE_KEY]
        log.VLOG('army: {:20s} number: {:8d}'.format(creature.get_name(), army[_ARMY_NUM_KEY]))
        creature.display_creature()

def main():
    hero_lib = item_creator.ItemCreator(_HERO_KEY)
    hero_name = mio.choose_command(hero_lib.item_list())
    if hero_name in common.CMD_QUIT:
        return
    hero = Hero(hero_name)
    creature_cage = creature.CreatureCage()
    while True:
        log.VLOG('insert creatures army, press q to finish')
        creature_name = mio.choose_command(creature_cage.list_creatures())
        if creature_name in common.CMD_QUIT:
            break
        else:
            log.VLOG('insert creature number')
            number = int(mio.stdin().strip())
            hero.create_army(creature_cage.get_creature(creature_name), number)
    hero.display_hero()

if __name__ == '__main__':
    main()
