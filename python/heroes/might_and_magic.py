#!/usr/bin/env python
# coding=utf-8
'''
heroes of might and magic class
Magtroid @ 2019-04-15 20:05
'''

import hero_config
import battle_field
import common
import creature
import hero
import item_creator
import log
import mio

def main():
    my_battle = battle_field.BattleField()
    hero_name = mio.choose_command(hero.hero_tavern.list_heroes())
    if hero_name in common.CMD_QUIT:
        return
    my_hero = hero.hero_tavern.get_hero(hero_name)

    hero_name = mio.choose_command(hero.hero_tavern.list_heroes())
    if hero_name in common.CMD_QUIT:
        return
    enemy_hero = hero.hero_tavern.get_hero(hero_name)

    my_battle.insert_hero(my_hero, enemy_hero)
    my_battle.battle_display()

if __name__ == '__main__':
    main()
