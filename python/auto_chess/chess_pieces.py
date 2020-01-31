#!/usr/bin/env python
# coding=utf-8
'''
chess pieces class
Magtroid @ 2019-10-15 17:31
'''

import auto_chess_config
import auto_chess_list
import common
import copy
import datalib
import log
import mio
import mtimer
import tools

FILTER_KEY = '__filter__'

_PIECE_KEY = 'chess_piece'
_COMBINE_KEY = 'chess_combine'

_COMBINE_SPECIES_KEY = 'species'
_COMBINE_PROFESSION_KEY = 'profession'
_COMBINE_TYPE = [_COMBINE_SPECIES_KEY, _COMBINE_PROFESSION_KEY]

_COMBINE_PIECES_KEY = 'combine_pieces'
_COMBINE_BUFF_KEY = 'combine_buff'

_BUFF_NUM_OFF = 0
_BUFF_CONTENT_OFF = 1

_NAME_KEY = 'name'
_COST_KEY = 'cost'
_ATTACK_KEY = 'attack'
_MIN_ATTACK_KEY = 'min_attack'
_MAX_ATTACK_KEY = 'max_attack'
_ARMOR_KEY = 'armor'
_ATTACK_SPEED_KEY = 'attack_speed'
_ATTACK_RANGE_KEY = 'attack_range'
_HEALTH_KEY = 'health'
_MANA_KEY = 'mana'

_LEVEL_1 = '★'
_LEVEL_2 = '★★'
_LEVEL_3 = '★★★'
_LEVELS = [_LEVEL_1, _LEVEL_2, _LEVEL_3]
_PROP_OFF = 0
_TYPE_OFF = 1
_CHESS_PROPERTIES = [_NAME_KEY, _COMBINE_SPECIES_KEY, _COMBINE_PROFESSION_KEY, _COST_KEY] + _LEVELS
_PROPERTIES = [[_MIN_ATTACK_KEY, common.TYPE_INT], [_MAX_ATTACK_KEY, common.TYPE_INT],
        [_ARMOR_KEY, common.TYPE_INT], [_ATTACK_SPEED_KEY, common.TYPE_FLOAT],
        [_ATTACK_RANGE_KEY, common.TYPE_INT], [_HEALTH_KEY, common.TYPE_INT],
        [_MANA_KEY, common.TYPE_INT]]

_DATA_ORI_KEY = [_NAME_KEY, datalib.DATA_FEATURE]

_FILTER_TYPE = _COMBINE_TYPE + [_COST_KEY]

_COMBINE_NEED_NUM = 'combine_need_num'
_COMBINE_EXIST_NUM = 'combine_exist_num'
_COMBINE_BUFF = 'combine_buff'

_MEM_NUM_FILTER = [[1], [1, 2], [1, 2], [1, 2, 3],
        [1, 2, 3], [1, 2, 3, 4], [1, 2, 3, 4]]
_SCORE_MAP = [0, 1.5, 2, 3, 5.2, 6, 8.5, 10, 12, 15, 18]
_SPECIAL_SCORE = {'异虫' : 0}

def create_combine_buff(need, exist, buff_content):
    buff = dict()
    buff[_COMBINE_NEED_NUM] = need
    buff[_COMBINE_EXIST_NUM] = exist
    buff[_COMBINE_BUFF] = buff_content
    return buff

def display_combine_buff(combine_buff):
    if combine_buff[_COMBINE_NEED_NUM]:
        return '{}({}): {}'.format(combine_buff[_COMBINE_NEED_NUM], combine_buff[_COMBINE_EXIST_NUM], combine_buff[_COMBINE_BUFF])
    else:
        return '({})'.format(combine_buff[_COMBINE_EXIST_NUM])

def get_combines_score(combines):
    score = 0
    for comb_type in combines.values():
        for key, combine in comb_type.items():
            if key in _SPECIAL_SCORE:
                score += _SPECIAL_SCORE[key]
            else:
                score += _SCORE_MAP[combine[_COMBINE_NEED_NUM]]
    return score

class ChessPieces(object):
    '''
    public:
      process_chess
      get_filter
      member_num_filter
      get_pieces
      team_combines
      combine_buff
    private:
      __process_chess_pieces
      __create_chess_piece
      __delete_chess_piece
      __modify_chess_piece
      __modify_chess_piece_prop
      __get_piece
      __get_combines
      __choose_combines
      __process_chess_combines
      __process_chess_combine
      __create_chess_combine
      __delete_chess_combine
      __modify_chess_combine
      __insert_combine_piece
      __delete_combine_piece
      __update_combine_piece
      __display_piece
      __display_combine
      __write_data_lib
    '''

    def __init__(self, name):
        self.__chess_pieces_path = tools.join_path([auto_chess_config.DATALIB, '{}.lib'.format(name)])
        self.__disable_controler = True
        self.__chess_pieces_data_lib = datalib.DataLib(self.__chess_pieces_path, self.__disable_controler)
        self.__chess_pieces_data_lib.load_data_lib()

    def process_chess(self):
        while True:
            command = mio.choose_command([_PIECE_KEY, _COMBINE_KEY])
            if command == _PIECE_KEY:
                self.__process_chess_pieces()
            elif command == _COMBINE_KEY:
                self.__process_chess_combines()
            else:
                break
        self.__write_data_lib()

    def get_filter(self):
        filt = dict()
        filt_type = mio.choose_command(_FILTER_TYPE)
        if filt_type in common.CMD_QUIT:
            return
        elif filt_type == _COST_KEY:
            log.VLOG('insert {} filter, multi number use , to split'.format(filt_type))
            cost = mio.stdin().strip()
            if cost in common.CMD_QUIT:
                return
            filt[_COST_KEY] = list(map(int, cost.split(',')))
            return filt
        elif filt_type in _COMBINE_TYPE:
            comb = mio.choose_command(self.__get_combines(filt_type))
            if comb in common.CMD_QUIT:
                return
            filt[filt_type] = comb
            return filt

    def member_num_filter(self, member_num):
        filt = dict()
        if member_num <= len(_MEM_NUM_FILTER):
            filt[_COST_KEY] = _MEM_NUM_FILTER[member_num - 1]
        return filt

    def get_pieces(self, filts = None):
        piece_data = self.__chess_pieces_data_lib.get_data(datalib.form_lkey([datalib.DATA_KEY, _PIECE_KEY]))
        if not piece_data:
            return []
        if filts is None:
            return list(piece_data)
        piece_data_filt = copy.deepcopy(piece_data)
        for filt, value in filts.items():
            piece_data_tmp = dict()
            for data_name, data_value in piece_data_filt.items():
                if filt not in data_value:
                    continue
                if isinstance(data_value[filt], list) and value in data_value[filt]:
                    piece_data_tmp[data_name] = data_value
                elif isinstance(data_value[filt], int) and data_value[filt] in value:
                    # cost filter
                    piece_data_tmp[data_name] = data_value
            piece_data_filt = copy.deepcopy(piece_data_tmp)
        return list(piece_data_filt.keys())

    def team_combines(self, team):
        combines = dict()
        for piece in team:
            piece_data = self.__get_piece(piece)
            if not piece_data:
                continue
            for comb_type in _COMBINE_TYPE:
                if comb_type not in combines:
                    combines[comb_type] = dict()
                combs = piece_data[comb_type]
                for comb in combs:
                    if comb not in combines[comb_type]:
                        combines[comb_type][comb] = 0
                    combines[comb_type][comb] += 1
        return combines

    def combine_buff(self, combines):
        combined = dict()
        not_combined = dict()
        for comb_type in combines:
            comb_type_dict = dict()
            not_comb_type_dict = dict()
            if not self.__chess_pieces_data_lib.lhas_key(datalib.form_lkey([datalib.DATA_KEY, _COMBINE_KEY, comb_type])):
                continue
            combs = combines[comb_type]
            for comb_key, comb_num in combs.items():
                comb_data = self.__get_combine(comb_type, comb_key)
                if not comb_data:
                    continue
                for i in range(comb_num, 0, -1):
                    if str(i) in comb_data[_COMBINE_BUFF_KEY]:
                        comb_type_dict[comb_key] = create_combine_buff(i, comb_num, comb_data[_COMBINE_BUFF_KEY][str(i)])
                        break
                else:
                    not_comb_type_dict[comb_key] = create_combine_buff(0, comb_num, '')
            combined[comb_type] = comb_type_dict
            not_combined[comb_type] = not_comb_type_dict
        return combined, not_combined


    def __get_piece(self, piece_name):
        return self.__chess_pieces_data_lib.get_data(datalib.form_lkey([datalib.DATA_KEY, _PIECE_KEY, piece_name]))

    def __get_combine(self, comb_type, comb_name):
        return self.__chess_pieces_data_lib.get_data(datalib.form_lkey([datalib.DATA_KEY, _COMBINE_KEY, comb_type, comb_name]))

    def __get_combines(self, comb_type):
        comb_data = self.__chess_pieces_data_lib.get_data(datalib.form_lkey([datalib.DATA_KEY, _COMBINE_KEY, comb_type]))
        if not comb_data:
            return []
        return list(comb_data.keys())


    def __process_chess_pieces(self):
        while True:
            species_name = mio.choose_command(self.get_pieces() + [common.NEW_KEY])
            if species_name in common.CMD_QUIT:
                break
            elif species_name == common.NEW_KEY:
                self.__create_chess_piece()
            else:
                self.__modify_chess_piece(species_name)

    def __create_chess_piece(self):
        piece = dict()
        # insert name
        log.VLOG('insert {}'.format(_NAME_KEY))
        piece_name = mio.stdin().strip()
        if piece_name in common.CMD_QUIT:
            return
        piece[_NAME_KEY] = piece_name

        # insert cost
        log.VLOG('insert {}'.format(_COST_KEY))
        cost = mio.stdin().strip()
        if cost in common.CMD_QUIT:
            return
        piece[_COST_KEY] = int(cost)

        # insert species
        status, species, new_species = self.__choose_combines(_COMBINE_SPECIES_KEY)
        if not status:
            return
        piece[_COMBINE_SPECIES_KEY] = species + new_species

        # insert profession
        status, professions, new_professions = self.__choose_combines(_COMBINE_PROFESSION_KEY)
        if not status:
            return
        piece[_COMBINE_PROFESSION_KEY] = professions + new_professions

        for level in _LEVELS:
            log.VLOG('{}: '.format(level))
            piece_level = dict()
            for prop in _PROPERTIES:
                log.VLOG('insert {}: '.format(prop[_PROP_OFF]))
                value = tools.change_format(mio.stdin().strip(), prop[_TYPE_OFF])
                piece_level[prop[_PROP_OFF]] = value
            piece[level] = piece_level
        self.__chess_pieces_data_lib.insert_data(_PIECE_KEY, piece, _NAME_KEY)

        if new_species:
            for new_spec in new_species:
                self.__create_chess_combine(_COMBINE_SPECIES_KEY, new_spec)
                species.append(new_spec)
        for spec in species:
            self.__insert_combine_piece(_COMBINE_SPECIES_KEY, spec, piece_name)
        if new_professions:
            for new_profession in new_professions:
                self.__create_chess_combine(_COMBINE_PROFESSION_KEY, new_profession)
                professions.append(new_profession)
        for profession in professions:
            self.__insert_combine_piece(_COMBINE_PROFESSION_KEY, profession, piece_name)

    def __delete_chess_piece(self):
        data = self.__chess_pieces_data_lib.get_data()
        if _PIECE_KEY not in data:
            log.VLOG('no piece in chess')
            return
        chess_pieces_data = data[_PIECE_KEY]
        name = mio.choose_command(list(chess_pieces_data.keys()))
        if name in common.CMD_QUIT:
            return
        log.INFO('do you want to remove piece: {}'.format(name))
        confirm = mio.choose_command(common.YON_COMMAND)
        if confirm == common.Y_COMMAND:
            self.__chess_pieces_data_lib.delete_data(datalib.form_lkey([_PIECE_KEY, name]))

    def __modify_chess_piece(self, name = None):
        if name is None:
            pieces_list = self.get_pieces()
            if not pieces_list:
                return
            name = mio.choose_command(pieces_list)
            if name in common.CMD_QUIT:
                return
        elif not self.__chess_pieces_data_lib.lhas_key(datalib.form_lkey([datalib.DATA_KEY, _PIECE_KEY, name])):
            log.VLOG('{} not exists'.format(name))
            return
        while True:
            self.__display_piece(name)
            prop = mio.choose_command(_CHESS_PROPERTIES + [common.DEL_KEY])
            if prop in common.CMD_QUIT:
                return
            elif prop == common.DEL_KEY:
                self.__delete_chess_piece(name)
                break
            else:
                new_name = self.__modify_chess_piece_prop(name, prop)
                if new_name:
                    name = new_name

    def __modify_chess_piece_prop(self, name, prop):
        piece_data = self.__chess_pieces_data_lib.get_data(datalib.form_lkey([datalib.DATA_KEY, _PIECE_KEY, name]))
        if prop == _NAME_KEY:
            log.VLOG('insert {}: '.format(prop))
            old_name = piece_data[prop]
            new_name = mio.stdin().strip()
            if new_name in common.CMD_QUIT:
                return
            if new_name in self.get_pieces():
                log.VLOG('{} exists'.format(new_name))
                return
            self.__chess_pieces_data_lib.set_data(datalib.form_lkey([datalib.DATA_KEY, _PIECE_KEY, name, prop]), new_name, is_id = True)
            self.__update_combine_piece(old_name, new_name)
            return new_name
        elif prop in _COMBINE_TYPE:
            status, combs, new_combs = self.__choose_combines(prop)
            if not status:
                return
            if new_combs:
                for new_comb in new_combs:
                    self.__create_chess_combine(prop, new_comb)
                    combs.append(new_comb)
            old_combs = piece_data[prop]
            for old_comb in old_combs:
                self.__delete_combine_piece(prop, old_comb, name)
            for new_comb in combs:
                self.__insert_combine_piece(prop, new_comb, name)
            piece_data[prop] = combs[:]
        elif prop == _COST_KEY:
            log.VLOG('insert {}: '.format(prop))
            cost = mio.stdin().strip()
            if cost in common.CMD_QUIT:
                return
            piece_data[prop] = int(cost)
        else:
            while True:
                self.__display_piece(name, level = prop)
                lprop = mio.choose_command(tools.colume(_PROPERTIES, _PROP_OFF))
                if lprop in common.CMD_QUIT:
                    break
                log.VLOG('insert {}: '.format(lprop))
                value = tools.change_format(mio.stdin().strip(), _PROPERTIES[[x[_PROP_OFF] for x in _PROPERTIES].index(lprop)][_TYPE_OFF])
                piece_data[prop][lprop] = value

    def __choose_combines(self, comb_type):
        combs = []
        new_combs = []
        while True:
            log.VLOG('insert {}: {}'.format(comb_type, tools.join_list(combs + new_combs)))
            comb = mio.choose_command(self.__get_combines(comb_type) + [common.NEW_KEY, common.CONFIRM_KEY])
            if comb in common.CMD_QUIT:
                return False, combs, new_combs
            elif comb == common.CONFIRM_KEY:
                log.VLOG('{} confirm?'.format(tools.join_list(combs + new_combs)))
                confirm = mio.choose_command(common.YON_COMMAND)
                if confirm == common.Y_COMMAND:
                    return True, combs, new_combs
            elif comb == common.NEW_KEY:
                log.VLOG('insert new {} name'.format(comb_type))
                new_comb = mio.stdin().strip()
                if new_comb in common.CMD_QUIT:
                    return False, combs, new_combs
                if new_comb in self.__get_combines(comb_type):
                    log.VLOG('{} exists'.format(new_comb))
                    return False, combs, new_combs
                new_combs.append(new_comb)
            else:
                combs.append(comb)

    def __process_chess_combines(self):
        while True:
            comb_type = mio.choose_command(_COMBINE_TYPE)
            if comb_type in common.CMD_QUIT:
                break
            while True:
                comb_name = mio.choose_command(self.__get_combines(comb_type) + [common.NEW_KEY])
                if comb_name in common.CMD_QUIT:
                    break
                elif comb_name == common.NEW_KEY:
                    self.__create_chess_combine(comb_type)
                else:
                    self.__process_chess_combine(comb_type, comb_name)

    def __process_chess_combine(self, comb_type, comb_name):
        while True:
            self.__display_combine(comb_type, comb_name)
            command = mio.choose_command([common.DEL_KEY, common.MOD_KEY])
            if command in common.CMD_QUIT:
                break
            elif command == common.DEL_KEY:
                self.__delete_chess_combine(comb_type, comb_name)
                break
            elif command == common.MOD_KEY:
                self.__modify_chess_combine(comb_type, comb_name)

    def __create_chess_combine(self, comb_type, name = None):
        comb = dict()
        if name is None:
            log.VLOG('insert new {} name: '.format(comb_type))
            name = mio.stdin().strip()
        if self.__chess_pieces_data_lib.lhas_key(datalib.form_lkey([datalib.DATA_KEY, _COMBINE_KEY, comb_type, name])):
            log.VLOG('{}: {} exists'.format(comb_type, name))
            return
        comb[_NAME_KEY] = name
        comb[_COMBINE_PIECES_KEY] = []
        comb[_COMBINE_BUFF_KEY] = dict()
        self.__chess_pieces_data_lib.insert_data(datalib.form_lkey([_COMBINE_KEY, comb_type]), comb, _NAME_KEY)

    def __delete_chess_combine(self, comb_type, name = None):
        if name is None:
            comb_list = self.__get_combines(comb_type)
            if not comb_list:
                return
            name = mio.choose_command(comb_list)
            if name in common.CMD_QUIT:
                return
        elif not self.__chess_pieces_data_lib.lhas_key(datalib.form_lkey([datalib.DATA_KEY, _COMBINE_KEY, comb_type, name])):
            log.VLOG('{}: {} not exists'.format(comb_type, name))
            return
        comb_data = self.__chess_pieces_data_lib.get_data(datalib.form_lkey([datalib.DATA_KEY, _COMBINE_KEY, comb_type, name]))
        if len(comb_data[_COMBINE_PIECES_KEY]) is not 0:
            log.VLOG('{}: {} not empty: {}'.format(comb_type, name, comb_data[_COMBINE_PIECES_KEY]))
            return
        log.INFO('do you want to remove {}: {}'.format(comb_type, name))
        confirm = mio.choose_command(common.YON_COMMAND)
        if confirm == common.Y_COMMAND:
            self.__chess_pieces_data_lib.delete_data(datalib.form_lkey([_COMBINE_KEY, comb_type, name]))

    def __modify_chess_combine(self, comb_type, name = None):
        if name is None:
            comb_list = self.__get_combines(comb_type)
            if not comb_list:
                return
            name = mio.choose_command(comb_list)
            if name in common.CMD_QUIT:
                return
        elif not self.__chess_pieces_data_lib.lhas_key(datalib.form_lkey([datalib.DATA_KEY, _COMBINE_KEY, comb_type, name])):
            log.VLOG('{}: {} not exists'.format(comb_type, name))
            return
        comb_buff = self.__chess_pieces_data_lib.get_data(datalib.form_lkey([datalib.DATA_KEY, _COMBINE_KEY, comb_type, name, _COMBINE_BUFF_KEY]))
        while True:
            self.__display_combine(comb_type, name)
            buff_name = mio.choose_command(list(comb_buff.keys()) + [common.NEW_KEY, common.DEL_KEY])
            if buff_name in common.CMD_QUIT:
                break
            elif buff_name == common.NEW_KEY:
                log.VLOG('insert buff number: ')
                number = mio.stdin().strip()
                log.VLOG('insert buff content: ')
                content = mio.stdin().strip()
                comb_buff[number] = content
            elif buff_name == common.DEL_KEY:
                if not comb_buff:
                    log.VLOG('no buff to delete')
                    continue
                prop = mio.choose_command(list(comb_buff.keys()))
                if prop in common.CMD_QUIT:
                    continue
                log.INFO('do you want to delete buff {}: {}'.format(prop, comb_buff[prop]))
                confirm = mio.choose_command(common.YON_COMMAND)
                if confirm == common.Y_COMMAND:
                    self.__chess_pieces_data_lib.delete_data(datalib.form_lkey([_COMBINE_KEY, comb_type, name, _COMBINE_BUFF_KEY, prop]))
            else:
                log.VLOG('insert buff {}: '.format(buff_name))
                comb_buff[buff_name] = mio.stdin().strip()

    def __insert_combine_piece(self, comb_type, comb_name, piece_name):
        combine = self.__chess_pieces_data_lib.get_data(datalib.form_lkey([datalib.DATA_KEY, _COMBINE_KEY, comb_type, comb_name]))
        if not combine:
            return
        if piece_name in combine[_COMBINE_PIECES_KEY]:
            return
        combine[_COMBINE_PIECES_KEY].append(piece_name)

    def __delete_combine_piece(self, comb_type, comb_name, piece_name):
        combine = self.__chess_pieces_data_lib.get_data(datalib.form_lkey([datalib.DATA_KEY, _COMBINE_KEY, comb_type, comb_name]))
        if not combine:
            return
        if piece_name not in combine[_COMBINE_PIECES_KEY]:
            return
        combine[_COMBINE_PIECES_KEY].remove(piece_name)

    def __update_combine_piece(self, old_name, new_name):
        for comb_type in _COMBINE_TYPE:
            comb_datas = self.__chess_pieces_data_lib.get_data(datalib.form_lkey([datalib.DATA_KEY, _COMBINE_KEY, comb_type]))
            for comb_name in comb_datas:
                comb_pieces = comb_datas[comb_name][_COMBINE_PIECES_KEY]
                for i in range(len(comb_pieces)):
                    if comb_pieces[i] == old_name:
                        comb_pieces[i] = new_name

    def __display_piece(self, name, level = None):
        if level is None:
            level = _LEVELS
        else:
            level = [level]
        piece_data = self.__chess_pieces_data_lib.get_data(datalib.form_lkey([datalib.DATA_KEY, _PIECE_KEY, name]))
        if not piece_data:
            return
        log.VLOG('{:10s} {:>6s}    {:12s} {:6d}'.format(_NAME_KEY, piece_data[_NAME_KEY], _COST_KEY, piece_data[_COST_KEY]))
        log.VLOG('{:10s} {:>6s}    {:12s} {:>6s}'.format(_COMBINE_SPECIES_KEY, tools.join_list(piece_data[_COMBINE_SPECIES_KEY]), _COMBINE_PROFESSION_KEY, tools.join_list(piece_data[_COMBINE_PROFESSION_KEY])))
        for clevel in level:
            level_data = piece_data[clevel]
            log.VLOG('{}'.format(clevel))
            log.VLOG('  {:12s} {:8d}    {:15s} {:3d}'.format(_HEALTH_KEY, level_data[_HEALTH_KEY], _ARMOR_KEY, level_data[_ARMOR_KEY]))
            log.VLOG('  {:12s} {:>8s}    {:15s} {:3.1f}'.format(_ATTACK_KEY, '{}~{}'.format(level_data[_MIN_ATTACK_KEY], level_data[_MAX_ATTACK_KEY]), _ATTACK_SPEED_KEY, level_data[_ATTACK_SPEED_KEY]))
            log.VLOG('  {:12s} {:8d}'.format(_ATTACK_RANGE_KEY, level_data[_ATTACK_RANGE_KEY]))

    def __display_combine(self, comb_type, name):
        data = self.__chess_pieces_data_lib.get_data(datalib.form_lkey([datalib.DATA_KEY, _COMBINE_KEY, comb_type, name]))
        if not data:
            log.VLOG('no combine: {} {}'.format(comb_type, name))
            return
        if data[_COMBINE_PIECES_KEY]:
            tools.print_list(data[_COMBINE_PIECES_KEY])
        for buff in data[_COMBINE_BUFF_KEY]:
            log.VLOG('{} {}: {}'.format(name, buff, data[_COMBINE_BUFF_KEY][buff]))

    def __write_data_lib(self):
        self.__chess_pieces_data_lib.write_data_lib()

if __name__ == '__main__':
    chess_list = auto_chess_list.AutoChessList()
    name = mio.choose_command(chess_list.list_chesses())
    if name not in common.CMD_QUIT:
        chess_pieces = ChessPieces(name)
        chess_pieces.process_chess()
