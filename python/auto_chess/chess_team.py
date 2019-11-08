#!/usr/bin/env python
# coding=utf-8
'''
chess team class
Magtroid @ 2019-11-05 15:54
'''

import auto_chess_config
import auto_chess_list
import chess_pieces
import common
import mio
import mmath
import log
import tools

_MAX_TEAM_MEMBER = 10
_FILTER_DEL = '__filt_del__'

_BACK_SEARCH_LEVEL = 3
_TOP_RECOMMEND_NUM = 10

class ChessTeam(object):
    '''
    public:
      build_chess_team
      recommend_team
    private:
      __team_full
      __recommend_team
      __recommend_filter
      __try_teams
      __judge_teams
      __display_filter
      __display_chess_team
    '''

    def __init__(self, name):
        self.__chess_pieces = chess_pieces.ChessPieces(name)
        self.__team = []
        self.__filter = dict()
        self.__recommend_teams = []

    def build_chess_team(self):
        while True:
            self.__display_chess_team()
            log.VLOG('{}'.format(tools.join_list(self.__team)))
            self.__display_filter()
            piece = mio.choose_command(list(set(self.__chess_pieces.get_pieces(filts = self.__filter)) - set(self.__team)) + [common.CONFIRM_KEY, common.DEL_KEY, chess_pieces.FILTER_KEY, _FILTER_DEL])
            if piece in common.CMD_QUIT:
                break
            elif piece == chess_pieces.FILTER_KEY:
                filt = self.__chess_pieces.get_filter()
                if not filt:
                    continue
                self.__filter.update(filt)
            elif piece == _FILTER_DEL:
                filt = mio.choose_command(list(self.__filter))
                if filt in common.CMD_QUIT:
                    continue
                self.__filter.pop(filt)
            elif piece == common.CONFIRM_KEY:
                log.VLOG('{} confirm?'.format(tools.join_list(self.__team)))
                confirm = mio.choose_command(common.YON_COMMAND)
                if confirm == common.Y_COMMAND:
                    self.__display_chess_team()
                    self.__filter.clear()
                    break
            elif piece == common.DEL_KEY:
                del_piece = mio.choose_command(self.__team)
                if del_piece in common.CMD_QUIT:
                    continue
                self.__team.remove(del_piece)
            else:
                if self.__team_full():
                    log.VLOG('team member full')
                    continue
                self.__team.append(piece)

    def recommend_team(self):
        self.build_chess_team()
        log.VLOG('insert member number')
        member_num = int(mio.stdin().strip())
        self.__recommend_filter(member_num)
        self.__recommend_team(member_num = member_num)
        while True:
            recommend = mio.choose_command(list(map(str, range(1, member_num + 1))))
            if recommend in common.CMD_QUIT:
                return
            for team in self.__recommend_teams[int(recommend)]:
                self.__display_chess_team(chess_team = team)

    def __team_full(self):
        return True if len(self.__team) >= _MAX_TEAM_MEMBER else False

    def __recommend_team(self, team = None, member_num = _MAX_TEAM_MEMBER):
        if team is None:
            team = self.__team
        for num in range(member_num + 1):
            if num < len(team):
                self.__recommend_teams.append([])
            elif num == len(team):
                self.__recommend_teams.append([team])
            else:
                log.VLOG('processing {} team members'.format(num))
                new_recommend_teams = []
                for level in range(1, _BACK_SEARCH_LEVEL + 1):
                    if num - level < 0:
                        continue
                    recommend_teams = self.__recommend_teams[num - level]
                    new_recommend_teams = tools.delete_duplicate(new_recommend_teams + self.__try_teams(recommend_teams, level))
                self.__recommend_teams.append(self.__judge_teams(new_recommend_teams))

    def __recommend_filter(self, member_num):
        self.__filter.update(self.__chess_pieces.member_num_filter(member_num))

    def __try_teams(self, recommend_teams, level):
        log.VLOG('begin to try teams')
        new_recommend_teams = []
        for recommend_team in recommend_teams:
            candidate = list(set(self.__chess_pieces.get_pieces(filts = self.__filter)) - set(recommend_team))
            log.VLOG('caculating permutation')
            candidate_combs = mmath.c(candidate, level)
            for n, candidate_comb in enumerate(candidate_combs):
                tools.schedule(n + 1, len(candidate_combs))
                new_recommend_teams.append(recommend_team + candidate_comb)
        log.VLOG('try teams finished')
        return new_recommend_teams

    def __judge_teams(self, recommend_teams):
        log.VLOG('begin to judge teams')
        top_recommend = mmath.TopNQ(_TOP_RECOMMEND_NUM)
        for n, recommend_team in enumerate(recommend_teams):
            tools.schedule(n + 1, len(recommend_teams))
            team_combs = self.__chess_pieces.team_combines(recommend_team)
            combined, not_combined = self.__chess_pieces.combine_buff(team_combs)
            combine_score = chess_pieces.get_combines_score(combined)
            top_recommend.insert(recommend_team, combine_score)
        log.VLOG('judge teams finished')
        return top_recommend.list()

    def __display_filter(self):
        if not self.__filter:
            return
        log.VLOG('filter: {}'.format(' '.join(['{}: {}'.format(x, y) for x, y in self.__filter.items()])))

    def __display_chess_team(self, chess_team = None):
        if chess_team is None:
            chess_team = self.__team
        log.VLOG('your team: {}'.format(tools.join_list(chess_team)))
        team_combines = self.__chess_pieces.team_combines(chess_team)
        combined, not_combined = self.__chess_pieces.combine_buff(team_combines)
        log.VLOG('joined combines:')
        for comb_type in combined.values():
            for comb_key, comb_buff in comb_type.items():
                log.VLOG('  {} {}'.format(comb_key, chess_pieces.display_combine_buff(comb_buff)))
        log.VLOG('not combined:')
        for comb_type in not_combined.values():
            for comb_key, comb_buff in comb_type.items():
                log.VLOG('  {} {}'.format(comb_key, chess_pieces.display_combine_buff(comb_buff)))
        log.VLOG()

if __name__ == '__main__':
    chess_list = auto_chess_list.AutoChessList()
    name = mio.choose_command(chess_list.list_chesses())
    if name not in common.CMD_QUIT:
        chess_team = ChessTeam(name)
        chess_team.build_chess_team()
