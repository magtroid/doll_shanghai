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

class Hero(object):
    '''
    public:
    private:
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

    def display_hero(self):
        log.VLOG('hero name: {}'.format(self.__name))
        log.VLOG('attack:     {:4d}  defence:   {:4d}'.format(self.__attack, self.__defence))
        log.VLOG('spellpower: {:4d}  knowledge: {:4d}'.format(self.__attack, self.__defence))

def main():
    hero_lib = item_creator.ItemCreator(_HERO_KEY)
    hero_name = mio.choose_command(hero_lib.item_list())
    if hero_name in common.CMD_QUIT:
        return
    hero = Hero(hero_name)
    hero.display_hero()

if __name__ == '__main__':
    main()
