#!/usr/bin/env python
# coding=utf-8
'''
hero class
Magtroid @ 2019-04-11 17:14
'''

import hero_config
import common
import copy
import creature
import datalib
import item_creator
import log
import mio
import tools

_HERO_KEY = 'hero'

# hero properties
_ATTACK_KEY = 'attack'
_DEFENCE_KEY = 'defence'
_SPELLPOWER_KEY = 'spellpower'
_KNOWLEDGE_KEY = 'knowledge'

# army properties
_MAX_ARMY_NUM = 7
ARMY_NUM_KEY = 'army_num'
ARMY_CREATURE_KEY = 'army_creature'

class Hero(object):
    '''
    public:
      create_army
      get_army
      display_hero
    private:
      __equipment_army
      __equipment_one_army
      __display_army
      __write_data_lib
    '''

    def __init__(self, name, hero_data = None):
        if hero_data is None:
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
        army[ARMY_NUM_KEY] = num
        army[ARMY_CREATURE_KEY] = creature
        self.__equipment_one_army(army)
        self.__army.append(army)

    def get_army(self):
        return self.__army

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
        army[ARMY_CREATURE_KEY].set_equipment_attack(self.__attack)
        army[ARMY_CREATURE_KEY].set_equipment_defence(self.__defence)

    def __display_army(self, army):
        creature = army[ARMY_CREATURE_KEY]
        log.VLOG('army: {:20s} number: {:8d}'.format(creature.get_name(), army[ARMY_NUM_KEY]))
        creature.display_creature()

_DEFAULT_ARMY_NUM = 2
_MAX_ARMY_NUM = 20

class Tavern(object):
    '''
    public:
      list_heroes
      get_hero
    private:
      __init_heroes
      __init_hero_army
    '''

    def __init__(self):
        self.__hero_lib = item_creator.ItemCreator(_HERO_KEY)
        self.__heroes = dict()
        self.__init_heroes()

    def list_heroes(self):
        return list(self.__heroes.keys())

    def get_hero(self, hero_name):
        if hero_name not in self.__heroes.keys():
            log.VLOG('hero: {} not exist'.format(hero_name))
            return dict()
        return copy.deepcopy(self.__heroes[hero_name])

    def __init_heroes(self):
        hero_list = self.__hero_lib.item_list()
        for hero_name in hero_list:
            hero_data = self.__hero_lib.get_item(hero_name)
            hero = Hero(hero_name, hero_data = hero_data)
            self.__init_hero_army(hero)
            self.__heroes[hero_name] = hero

    def __init_hero_army(self, hero):
        for i in range(_DEFAULT_ARMY_NUM):
            creatures = creature.creature_cage.list_creatures()
            creature_name = tools.random_choose(creatures)
            creature_num = int(tools.mrandom(_MAX_ARMY_NUM))
            hero.create_army(creature.creature_cage.get_creature(creature_name), creature_num)

hero_tavern = Tavern()

def main():
    hero_name = mio.choose_command(hero_tavern.list_heroes())
    if hero_name in common.CMD_QUIT:
        return
    hero = hero_tavern.get_hero(hero_name)
    hero.display_hero()

if __name__ == '__main__':
    main()
