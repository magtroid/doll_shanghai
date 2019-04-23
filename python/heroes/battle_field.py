#!/usr/bin/env python
# coding=utf-8
'''
battle field class
Magtroid @ 2019-04-12 18:12
'''

import hero_config
import canvas
import common
import copy
import hero
import log
import mio
import music
import tools

_COORD_Y = 0
_COORD_X = 1
# battle structure
_BATTLE_KEY = 'battle'
_BATTLE_MATRIX = [8, 12]
_BATTLE_UNIT_SIZE = [3, 7]
_BATTLE_HEIGHT = _BATTLE_MATRIX[_COORD_Y] * _BATTLE_UNIT_SIZE[_COORD_Y] + _BATTLE_MATRIX[_COORD_Y] + 1
_BATTLE_WIDTH = _BATTLE_MATRIX[_COORD_X] * _BATTLE_UNIT_SIZE[_COORD_X] + _BATTLE_MATRIX[_COORD_X] + 1
_BATTLE_STRUCTURE = [[0, _BATTLE_HEIGHT, _BATTLE_WIDTH]]

_CURSOR_KEY = 'cursor'
_CURSOR_LINE_INIT = 1
_CURSOR_STRUCTURE = [[1, _BATTLE_UNIT_SIZE[_COORD_Y], _BATTLE_UNIT_SIZE[_COORD_X]]]

# army status structure
_ARMY_STATUS_KEY = 'army_status'
_ARMY_STATUS_STRUCTURE = [[_BATTLE_WIDTH + 1, 10, 50]]

# battle command
_BATTLE_GRID_ON = '+'
_BATTLE_GRID_OFF = '-'
_BATTLE_COMMANDS = [common.UP_KEY, common.DOWN_KEY, common.LEFT_KEY, common.RIGHT_KEY, _BATTLE_GRID_ON, _BATTLE_GRID_OFF]

# hero
_ATTACK_ARMY_COORD = [0, 0]
_DEFENCE_ARMY_COORD = [0, _BATTLE_MATRIX[_COORD_X] - 1]
_ATTACK_ARMY_KEY = 'attack'
_DEFENCE_ARMY_KEY = 'defence'

# battle board
_ARMY_NAME_KEY = 'name'
_BATTLE_ARMY_KEY = 'army'

# battle music
_ATTACK_HEAVEN_TOWN = 'Siege-Haven'

# battle begin
_SELECT_MODULE = 'select_module'
_VIEW_MODULE = 'view_module'

class BattleField(object):
    '''
    public:
      insert_hero
      battle_display
    private:
      __check_terminal_size
      __paint_battle_field
      __paint_cursor
      __embattle
      __embattle_init
      __embattle_adjust
      __create_battle_army
      __move_battle_board
      __paint_hero
      __paint_army
      __move_army
      __paint_status
      __battle_coord_to_point_coord
      __battle_finish
    '''

    def __init__(self):
        if not self.__check_terminal_size():
            return
        self.__grid = False
        self.__canvas = canvas.CANVAS()
        self.__canvas.new_area(_BATTLE_STRUCTURE, name = _BATTLE_KEY)
        self.__canvas.new_area(_ARMY_STATUS_STRUCTURE, name = _ARMY_STATUS_KEY)
        self.__canvas.new_area(_CURSOR_STRUCTURE, line = _CURSOR_LINE_INIT, name = _CURSOR_KEY)
        self.__cursor_coord = [0, 0]
        self.__attack_hero = dict()
        self.__attack_army = []
        self.__defence_hero = dict()
        self.__defence_army = []
        self.__status_coord = []
        # should use for instead of * to init list, otherwise change one item, all other will change
        self.__battle_board = [[dict() for col in range(_BATTLE_MATRIX[_COORD_X])] for row in range(_BATTLE_MATRIX[_COORD_Y])]
        self.__module = _VIEW_MODULE

        self.__paint_battle_field()
        self.__paint_cursor()

    def insert_hero(self, attack_hero, defence_hero):
        self.__attack_hero = copy.deepcopy(attack_hero)
        self.__attack_army = copy.deepcopy(attack_hero.get_army())
        self.__defence_hero = copy.deepcopy(defence_hero)
        self.__defence_army = copy.deepcopy(defence_hero.get_army())
        self.__embattle()
        self.__paint_hero()
        self.__paint_army()

    def battle_display(self):
        self.__canvas.display()
        music.play(_ATTACK_HEAVEN_TOWN)
        while True:
            # command = mio.choose_command(_BATTLE_COMMANDS, print_log = False)
            command = mio.kbhit(refresh_times = 10)
            if command in common.CMD_QUIT:
                break
            elif command == common.UP_KEY:
                if self.__cursor_coord[_COORD_Y] > 0:
                    self.__cursor_coord[_COORD_Y] -= 1
                    coord = [-_BATTLE_UNIT_SIZE[_COORD_Y] - 1, 0]
                    self.__canvas.move_area(_CURSOR_KEY, coord)
            elif command == common.DOWN_KEY:
                if self.__cursor_coord[_COORD_Y] < _BATTLE_MATRIX[_COORD_Y] - 1:
                    self.__cursor_coord[_COORD_Y] += 1
                    coord = [_BATTLE_UNIT_SIZE[_COORD_Y] + 1, 0]
                    self.__canvas.move_area(_CURSOR_KEY, coord)
            elif command == common.LEFT_KEY:
                if self.__cursor_coord[_COORD_X] > 0:
                    self.__cursor_coord[_COORD_X] -= 1
                    coord = [0, -_BATTLE_UNIT_SIZE[_COORD_X] - 1]
                    self.__canvas.move_area(_CURSOR_KEY, coord)
            elif command == common.RIGHT_KEY:
                if self.__cursor_coord[_COORD_X] < _BATTLE_MATRIX[_COORD_X] - 1:
                    self.__cursor_coord[_COORD_X] += 1
                    coord = [0, _BATTLE_UNIT_SIZE[_COORD_X] + 1]
                    self.__canvas.move_area(_CURSOR_KEY, coord)
            elif command == _BATTLE_GRID_ON:
                prev_grid = self.__grid
                self.__grid = True
                if not prev_grid:
                    self.__paint_battle_field()
                    self.__paint_cursor()
            elif command == _BATTLE_GRID_OFF:
                prev_grid = self.__grid
                self.__grid = False
                if prev_grid:
                    self.__paint_battle_field()
                    self.__paint_cursor()
            if self.__module == _VIEW_MODULE:
                if command == common.BLANK_KEY:
                    self.__paint_status()
            else:  # _SELECT_MODULE
                if command == common.BLANK_KEY:
                    self.__move_army()
                elif command == common.ESC_KEY:
                    self.__module = _VIEW_MODULE
            self.__canvas.display()
        self.__battle_finish()

    def __check_terminal_size(self):
        height, width = tools.get_terminal_size()
        if height < _BATTLE_HEIGHT or width < _BATTLE_WIDTH:
            log.VLOG('terminal size is small {} X {} (should be at least {} X {})'.format(height, width,
                                                                                          _BATTLE_HEIGHT,
                                                                                          _BATTLE_WIDTH))
            return False
        return True

    def __paint_battle_field(self):
        self.__canvas.clear_area()
        self.__canvas.paint('┌{}┐'.format('─' * (_BATTLE_WIDTH - 2)), name = _BATTLE_KEY)
        for i in range(1, _BATTLE_HEIGHT - 1):
            self.__canvas.paint('│', coordinate = [i, 0], name = _BATTLE_KEY)
            self.__canvas.paint('│', coordinate = [i, _BATTLE_WIDTH - 1], name = _BATTLE_KEY)
        self.__canvas.paint('└{}┘'.format('─' * (_BATTLE_WIDTH - 2)), coordinate = [_BATTLE_HEIGHT - 1, 0], name = _BATTLE_KEY)
        if self.__grid:
            for i in range(1, _BATTLE_MATRIX[_COORD_Y]):
                self.__canvas.paint('├{}┤'.format('─' * (_BATTLE_WIDTH - 2)), coordinate = [(_BATTLE_UNIT_SIZE[_COORD_Y] + 1) * i, 0], name = _BATTLE_KEY)
            for i in range(1, _BATTLE_MATRIX[_COORD_X]):
                self.__canvas.paint('┬', coordinate = [0, (_BATTLE_UNIT_SIZE[_COORD_X] + 1) * i], name = _BATTLE_KEY)
                for j in range(1, _BATTLE_HEIGHT - 1):
                    if j % (_BATTLE_UNIT_SIZE[_COORD_Y] + 1) == 0:
                        paint_str = '┼'
                    else:
                        paint_str = '│'
                    self.__canvas.paint(paint_str, coordinate = [j, (_BATTLE_UNIT_SIZE[_COORD_X] + 1) * i], name = _BATTLE_KEY)
                self.__canvas.paint('┴', coordinate = [_BATTLE_HEIGHT - 1, (_BATTLE_UNIT_SIZE[_COORD_X] + 1) * i], name = _BATTLE_KEY)

    def __paint_cursor(self):
        for i in range(_BATTLE_UNIT_SIZE[_COORD_Y]):
            self.__canvas.insert_format([i, 0, _BATTLE_UNIT_SIZE[_COORD_X]], back = canvas.WHITE, name = _CURSOR_KEY)

    def __embattle(self):
        self.__embattle_init()
        self.__embattle_adjust()

    def __embattle_init(self):
        attack_coord = _ATTACK_ARMY_COORD
        for i in range(len(self.__attack_army)):
            self.__battle_board[attack_coord[_COORD_Y]][attack_coord[_COORD_X]] = self.__create_battle_army(_ATTACK_ARMY_KEY + str(i), self.__attack_army[i])
            attack_coord[_COORD_Y] += 1
        defence_coord = _DEFENCE_ARMY_COORD
        for i in range(len(self.__defence_army)):
            self.__battle_board[defence_coord[_COORD_Y]][defence_coord[_COORD_X]] = self.__create_battle_army(_DEFENCE_ARMY_KEY + str(i), self.__defence_army[i])
            defence_coord[_COORD_Y] += 1

    def __embattle_adjust(self):
        return

    # battle army is a dict contain target army name and army self
    def __create_battle_army(self, name, army):
        battle_army = dict()
        battle_army[_ARMY_NAME_KEY] = name
        battle_army[_BATTLE_ARMY_KEY] = army
        return battle_army

    def __move_battle_board(self, coord_from, coord_to):
        self.__battle_board[coord_to[_COORD_Y]][coord_to[_COORD_X]] = copy.deepcopy(self.__battle_board[coord_from[_COORD_Y]][coord_from[_COORD_X]])
        self.__battle_board[coord_from[_COORD_Y]][coord_from[_COORD_X]] = dict()

    def __paint_hero(self):
        return

    def __paint_army(self):
        for y in range(len(self.__battle_board)):
            for x in range(len(self.__battle_board[y])):
                battle_army = self.__battle_board[y][x]
                if battle_army:
                    # print('{} {}'.format(y, x))
                    army_name = battle_army[_ARMY_NAME_KEY]
                    army_army = battle_army[_BATTLE_ARMY_KEY]
                    army_structure = [[x * (_BATTLE_UNIT_SIZE[_COORD_X] + 1) + 1, _BATTLE_UNIT_SIZE[_COORD_Y], _BATTLE_UNIT_SIZE[_COORD_X]]]
                    army_line = y * (_BATTLE_UNIT_SIZE[_COORD_Y] + 1) + 1
                    self.__canvas.new_area(army_structure, line = army_line, name = army_name)
                    self.__canvas.paint('{:{}d}'.format(army_army[hero.ARMY_NUM_KEY], _BATTLE_UNIT_SIZE[_COORD_X]), coordinate = [_BATTLE_UNIT_SIZE[_COORD_Y] - 1, 0], name = army_name)

    def __move_army(self):
        cursor_army = self.__battle_board[self.__cursor_coord[_COORD_Y]][self.__cursor_coord[_COORD_X]]
        if cursor_army:
            return
        coord_from = self.__battle_coord_to_point_coord(self.__status_coord)
        coord_to = self.__battle_coord_to_point_coord(self.__cursor_coord)
        coord_off = [coord_to[_COORD_Y] - coord_from[_COORD_Y], coord_to[_COORD_X] - coord_from[_COORD_X]]
        status_army = self.__battle_board[self.__status_coord[_COORD_Y]][self.__status_coord[_COORD_X]]
        self.__canvas.move_area(status_army[_ARMY_NAME_KEY], coord_off)
        self.__move_battle_board(self.__status_coord, self.__cursor_coord)
        self.__status_coord = self.__cursor_coord[:]

    def __paint_status(self):
        if self.__cursor_coord == self.__status_coord:
            self.__status_coord = []
            self.__canvas.clear_area(area_list = [_ARMY_STATUS_KEY])
        else:
            battle_army = self.__battle_board[self.__cursor_coord[_COORD_Y]][self.__cursor_coord[_COORD_X]]
            if battle_army:
                creature = battle_army[_BATTLE_ARMY_KEY][hero.ARMY_CREATURE_KEY]
                number = battle_army[_BATTLE_ARMY_KEY][hero.ARMY_NUM_KEY]
                ostr = ''
                ostr = log.VLOG('army: {:20s} number: {:8d}'.format(creature.get_name(), number), ostr = ostr)
                ostr = creature.display_creature(ostr = ostr)
                self.__canvas.clear_area(area_list = [_ARMY_STATUS_KEY])
                self.__canvas.paint(ostr, name = _ARMY_STATUS_KEY)
                self.__module = _SELECT_MODULE
            else:
                self.__canvas.clear_area(area_list = [_ARMY_STATUS_KEY])
            self.__status_coord = self.__cursor_coord[:]

    def __battle_coord_to_point_coord(self, battle_coord):
        return [battle_coord[_COORD_Y] * (_BATTLE_UNIT_SIZE[_COORD_Y] + 1) + 1, battle_coord[_COORD_X] * (_BATTLE_UNIT_SIZE[_COORD_X] + 1) + 1]

    def __battle_finish(self):
        music.stop()

def main():
    battle_field = BattleField()
    battle_field.battle_display()

if __name__ == '__main__':
    main()
