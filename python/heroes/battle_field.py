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
_BATTLE_COORD = [0, 0]
_BATTLE_STRUCTURE = [_BATTLE_HEIGHT, _BATTLE_WIDTH]

_CURSOR_KEY = 'cursor'
_CURSOR_COORD = [1, 1]
_CURSOR_STRUCTURE = [_BATTLE_UNIT_SIZE[_COORD_Y], _BATTLE_UNIT_SIZE[_COORD_X]]

# army status structure
_CUR_ARMY_STATUS_KEY = 'cur_army_status'
_CUR_ARMY_STATUS_COORD = [0, _BATTLE_WIDTH + 1]
_CUR_ARMY_STATUS_STRUCTURE = [10, 50]
_TAR_ARMY_STATUS_KEY = 'tar_army_status'
_TAR_ARMY_STATUS_COORD = [15, _BATTLE_WIDTH + 1]
_TAR_ARMY_STATUS_STRUCTURE = [10, 50]

# move queue
_MOVE_QUEUE_KEY = 'move_queue'
_MOVE_QUEUE_COORD = [_BATTLE_HEIGHT + 1, 0]
_MOVE_QUEUE_STRUCTURE = [_BATTLE_UNIT_SIZE[_COORD_Y] + 2, _BATTLE_WIDTH]

# battle command
_BATTLE_GRID_ON = '+'
_BATTLE_GRID_OFF = '-'
_BATTLE_ENTER_KEY = common.BLANK_KEY
_BATTLE_WAIT_KEY = 'wait'
_BATTLE_DEFENCE_KEY = 'defence'
_BATTLE_COMMANDS = [common.UP_KEY, common.DOWN_KEY, common.LEFT_KEY, common.RIGHT_KEY, _BATTLE_GRID_ON, _BATTLE_GRID_OFF,
                    _BATTLE_ENTER_KEY, _BATTLE_WAIT_KEY, _BATTLE_DEFENCE_KEY]

# hero
_ATTACK_ARMY_KEY = 'attack'
_DEFENCE_ARMY_KEY = 'defence'
_ARMY_GROUP_COORD = {_ATTACK_ARMY_KEY : 0, _DEFENCE_ARMY_KEY : _BATTLE_MATRIX[_COORD_X] - 1}

# battle board
_ARMY_NAME_KEY = 'name'
_ARMY_GROUP_KEY = 'group'
_ARMY_COORD_KEY = 'coord'
_ARMY_ATB_KEY = 'atb'
_BATTLE_ARMY_KEY = 'army'

# battle music
_ATTACK_HEAVEN_TOWN = 'Siege-Haven'

# battle begin
_SELECT_MODULE = 'select_module'

# atb step
_ATB_MAX_TIME = 999
_ATB_INIT_ID = 0
_ATB_STEP = 0.1

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
      __paint_move_queue
      __paint_move_queue_struct
      __paint_move_queue_army
      __paint_hero
      __paint_army
      __move_army
      __paint_cur_status
      __highlight_army
      __battle_coord_to_point_coord
      __next_move
      __battle_finish
    '''

    def __init__(self):
        if not self.__check_terminal_size():
            return
        self.__grid = False
        self.__canvas = canvas.CANVAS()
        self.__canvas.sub_canvas(_BATTLE_COORD, _BATTLE_STRUCTURE, name = _BATTLE_KEY)
        self.__canvas.sub_canvas(_CUR_ARMY_STATUS_COORD, _CUR_ARMY_STATUS_STRUCTURE, name = _CUR_ARMY_STATUS_KEY)
        self.__canvas.sub_canvas(_TAR_ARMY_STATUS_COORD, _TAR_ARMY_STATUS_STRUCTURE, name = _TAR_ARMY_STATUS_KEY)
        self.__canvas.sub_canvas(_CURSOR_COORD, _CURSOR_STRUCTURE, name = _CURSOR_KEY)
        self.__canvas.sub_canvas(_MOVE_QUEUE_COORD, _MOVE_QUEUE_STRUCTURE, name = _MOVE_QUEUE_KEY)
        self.__cursor_coord = [0, 0]
        self.__cur_status_coord = []
        self.__tar_status_coord = []
        self.__battle_army = []
        self.__attack_hero = dict()
        self.__defence_hero = dict()
        # should use for instead of * to init list, otherwise change one item, all other will change
        self.__battle_board = [[dict() for col in range(_BATTLE_MATRIX[_COORD_X])] for row in range(_BATTLE_MATRIX[_COORD_Y])]
        self.__move_queue = []

        self.__paint_battle_field()

    def insert_hero(self, attack_hero, defence_hero):
        self.__attack_hero = copy.deepcopy(attack_hero)
        self.__defence_hero = copy.deepcopy(defence_hero)
        self.__insert_battle_army(copy.deepcopy(attack_hero.get_army()), _ATTACK_ARMY_KEY)
        self.__insert_battle_army(copy.deepcopy(defence_hero.get_army()), _DEFENCE_ARMY_KEY)
        self.__embattle()
        self.__paint_hero()
        self.__paint_army()

    def battle_display(self):
        self.__paint_move_queue()
        self.__next_move()
        self.__paint_cursor()
        self.__canvas.display()
        music.play(_ATTACK_HEAVEN_TOWN)
        while True:
            command = mio.choose_command(_BATTLE_COMMANDS, block = False, print_log = False)
            # command = mio.kbhit(refresh_times = 10)
            if command in common.CMD_QUIT:
                break
            elif command == common.UP_KEY:
                if self.__cursor_coord[_COORD_Y] > 0:
                    self.__cursor_coord[_COORD_Y] -= 1
                    coord = [-_BATTLE_UNIT_SIZE[_COORD_Y] - 1, 0]
                    self.__canvas.move_sub_canvas(_CURSOR_KEY, coord)
            elif command == common.DOWN_KEY:
                if self.__cursor_coord[_COORD_Y] < _BATTLE_MATRIX[_COORD_Y] - 1:
                    self.__cursor_coord[_COORD_Y] += 1
                    coord = [_BATTLE_UNIT_SIZE[_COORD_Y] + 1, 0]
                    self.__canvas.move_sub_canvas(_CURSOR_KEY, coord)
            elif command == common.LEFT_KEY:
                if self.__cursor_coord[_COORD_X] > 0:
                    self.__cursor_coord[_COORD_X] -= 1
                    coord = [0, -_BATTLE_UNIT_SIZE[_COORD_X] - 1]
                    self.__canvas.move_sub_canvas(_CURSOR_KEY, coord)
            elif command == common.RIGHT_KEY:
                if self.__cursor_coord[_COORD_X] < _BATTLE_MATRIX[_COORD_X] - 1:
                    self.__cursor_coord[_COORD_X] += 1
                    coord = [0, _BATTLE_UNIT_SIZE[_COORD_X] + 1]
                    self.__canvas.move_sub_canvas(_CURSOR_KEY, coord)
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
            elif command == _BATTLE_ENTER_KEY:
                break
                # self.__process_enter()
                # self.__paint_status()
            # else:  # _SELECT_MODULE
            #     if command == common.BLANK_KEY:
            #         self.__move_army()
            #     elif command == common.ESC_KEY:
            #         self.__module = _VIEW_MODULE
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
        self.__canvas.erase()
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
            self.__canvas.dump(back = canvas.WHITE, name = _CURSOR_KEY)

    def __embattle(self):
        self.__embattle_init()
        self.__embattle_adjust()

    def __embattle_init(self):
        for army in self.__battle_army:
            self.__battle_board[army[_ARMY_COORD_KEY][_COORD_Y]][army[_ARMY_COORD_KEY][_COORD_X]] = army

    def __embattle_adjust(self):
        return

    def __insert_battle_army(self, army_list, group):
        for i in range(len(army_list)):
            self.__battle_army.append(self.__create_battle_army(group, i, army_list[i]))

    # battle army is a dict contain target army name and army self
    def __create_battle_army(self, group, army_id, army):
        battle_army = dict()
        battle_army[_ARMY_NAME_KEY] = group + str(army_id)
        battle_army[_ARMY_GROUP_KEY] = group
        battle_army[_ARMY_ATB_KEY] = tools.mrandom()
        battle_army[_ARMY_COORD_KEY] = [army_id, _ARMY_GROUP_COORD[group]]
        battle_army[_BATTLE_ARMY_KEY] = army
        return battle_army

    def __move_battle_board(self, coord_from, coord_to):
        self.__battle_board[coord_from[_COORD_Y]][coord_from[_COORD_X]][_ARMY_COORD_KEY] = coord_to[:]
        self.__battle_board[coord_to[_COORD_Y]][coord_to[_COORD_X]] = self.__battle_board[coord_from[_COORD_Y]][coord_from[_COORD_X]]
        self.__battle_board[coord_from[_COORD_Y]][coord_from[_COORD_X]] = dict()

    def __paint_move_queue(self):
        self.__paint_move_queue_struct()
        self.__gen_move_queue()
        self.__paint_move_queue_army()

    def __paint_move_queue_struct(self):
        self.__canvas.paint('┌{}┐'.format('─' * (_BATTLE_WIDTH - 2)), name = _MOVE_QUEUE_KEY)
        for i in range(1, _BATTLE_UNIT_SIZE[_COORD_Y] + 1):
            self.__canvas.paint('│', coordinate = [i, 0], name = _MOVE_QUEUE_KEY)
            self.__canvas.paint('│', coordinate = [i, _BATTLE_WIDTH - 1], name = _MOVE_QUEUE_KEY)
        self.__canvas.paint('└{}┘'.format('─' * (_BATTLE_WIDTH - 2)), coordinate = [_BATTLE_UNIT_SIZE[_COORD_Y] + 1, 0], name = _MOVE_QUEUE_KEY)
        for i in range(1, _BATTLE_MATRIX[_COORD_X]):
            self.__canvas.paint('┬', coordinate = [0, (_BATTLE_UNIT_SIZE[_COORD_X] + 1) * i], name = _MOVE_QUEUE_KEY)
            for j in range(1, _BATTLE_UNIT_SIZE[_COORD_Y] + 1):
                self.__canvas.paint('│', coordinate = [j, (_BATTLE_UNIT_SIZE[_COORD_X] + 1) * i], name = _MOVE_QUEUE_KEY)
            self.__canvas.paint('┴', coordinate = [_BATTLE_UNIT_SIZE[_COORD_Y] + 1, (_BATTLE_UNIT_SIZE[_COORD_X] + 1) * i], name = _MOVE_QUEUE_KEY)

    def __gen_move_queue(self):
        if not self.__battle_army:
            return
        atb_list = []
        for i in range(len(self.__battle_army)):
            atb_list.append(self.__battle_army[i][_ARMY_ATB_KEY])
        for i in range(_BATTLE_MATRIX[_COORD_X]):
            self.__move_queue.append(self.__gen_next_move(atb_list))

    def __gen_next_move(self, atb_list):
        if not atb_list:
            return
        min_time = _ATB_MAX_TIME
        min_id = _ATB_INIT_ID
        for i in range(len(atb_list)):
            time = (1 - atb_list[i]) / _ATB_STEP
            if time < min_time:
                min_time = time
                min_id = i
        # update atb
        for i in range(len(atb_list)):
            if i == min_id:
                atb_list[i] = 0
            else:
                atb_list[i] += min_time * _ATB_STEP
        return self.__battle_army[min_id]

    def __paint_move_queue_army(self):
        for i in range(len(self.__move_queue)):
            queue_coord = [_BATTLE_HEIGHT + 2, i * (_BATTLE_UNIT_SIZE[_COORD_X] + 1) + 1]
            queue_structure = [_BATTLE_UNIT_SIZE[_COORD_Y], _BATTLE_UNIT_SIZE[_COORD_X]]
            queue_name = _MOVE_QUEUE_KEY + str(i)
            self.__canvas.sub_canvas(queue_coord, queue_structure, name = queue_name)
            self.__canvas.paint('{:{}d}'.format(self.__move_queue[i][_BATTLE_ARMY_KEY][hero.ARMY_NUM_KEY], _BATTLE_UNIT_SIZE[_COORD_X]), coordinate = [_BATTLE_UNIT_SIZE[_COORD_Y] - 1, 0], name = queue_name)

    def __paint_hero(self):
        return

    def __paint_army(self):
        for y in range(len(self.__battle_board)):
            for x in range(len(self.__battle_board[y])):
                battle_army = self.__battle_board[y][x]
                if battle_army:
                    army_name = battle_army[_ARMY_NAME_KEY]
                    army_army = battle_army[_BATTLE_ARMY_KEY]
                    army_coord = [y * (_BATTLE_UNIT_SIZE[_COORD_Y] + 1) + 1, x * (_BATTLE_UNIT_SIZE[_COORD_X] + 1) + 1]
                    army_structure = [_BATTLE_UNIT_SIZE[_COORD_Y], _BATTLE_UNIT_SIZE[_COORD_X]]
                    self.__canvas.sub_canvas(army_coord, army_structure, name = army_name)
                    self.__canvas.paint('{:{}d}'.format(army_army[hero.ARMY_NUM_KEY], _BATTLE_UNIT_SIZE[_COORD_X]), coordinate = [_BATTLE_UNIT_SIZE[_COORD_Y] - 1, 0], name = army_name)

    def __move_army(self):
        cursor_army = self.__battle_board[self.__cursor_coord[_COORD_Y]][self.__cursor_coord[_COORD_X]]
        if cursor_army:
            return
        coord_from = self.__battle_coord_to_point_coord(self.__cur_status_coord)
        coord_to = self.__battle_coord_to_point_coord(self.__cursor_coord)
        coord_off = [coord_to[_COORD_Y] - coord_from[_COORD_Y], coord_to[_COORD_X] - coord_from[_COORD_X]]
        status_army = self.__battle_board[self.__cur_status_coord[_COORD_Y]][self.__cur_status_coord[_COORD_X]]
        self.__canvas.move_area(status_army[_ARMY_NAME_KEY], coord_off)
        self.__move_battle_board(self.__cur_status_coord, self.__cursor_coord)
        self.__cur_status_coord = self.__cursor_coord[:]

    def __paint_cur_status(self):
        battle_army = self.__battle_board[self.__cur_status_coord[_COORD_Y]][self.__cur_status_coord[_COORD_X]]
        if battle_army:
            creature = battle_army[_BATTLE_ARMY_KEY][hero.ARMY_CREATURE_KEY]
            number = battle_army[_BATTLE_ARMY_KEY][hero.ARMY_NUM_KEY]
            ostr = ''
            ostr = log.VLOG('army: {:20s} number: {:8d}'.format(creature.get_name(), number), ostr = ostr)
            ostr = creature.display_creature(ostr = ostr)
            self.__canvas.erase(name = _CUR_ARMY_STATUS_KEY)
            self.__canvas.paint(ostr, name = _CUR_ARMY_STATUS_KEY)
            self.__module = _SELECT_MODULE
        else:
            self.__canvas.erase(name = _CUR_ARMY_STATUS_KEY)
        self.__cur_status_coord = self.__cursor_coord[:]

    def __highlight_army(self, army):
        army_name = army[_ARMY_NAME_KEY]
        for i in range(_BATTLE_UNIT_SIZE[_COORD_Y]):
            self.__canvas.insert_format([i, 0, _BATTLE_UNIT_SIZE[_COORD_X]], front = canvas.WHITE, name = army_name)

    def __battle_coord_to_point_coord(self, battle_coord):
        return [battle_coord[_COORD_Y] * (_BATTLE_UNIT_SIZE[_COORD_Y] + 1) + 1, battle_coord[_COORD_X] * (_BATTLE_UNIT_SIZE[_COORD_X] + 1) + 1]

    def __next_move(self):
        if not self.__move_queue:
            return
        next_army = self.__move_queue[0]
        self.__cur_status_coord = next_army[_ARMY_COORD_KEY]
        self.__paint_cur_status()
        self.__highlight_army(next_army)

    def __battle_finish(self):
        music.stop()

def main():
    battle_field = BattleField()
    battle_field.battle_display()

if __name__ == '__main__':
    main()
