#!/usr/bin/env python
# coding=utf-8
'''
auto chess class
Magtroid @ 2019-10-15 17:31
'''

import auto_chess_list
import common
import chess_pieces
import chess_team
import log
import mio

_NEW_CHESS = '__new_chess__'
_BUILD_TEAM = '__build_team__'
_RECOMMEND_TEAM = '__recommend__'

def select_chess():
    chess_list = auto_chess_list.AutoChessList()
    log.VLOG('choose a chess')
    chess = mio.choose_command(chess_list.list_chesses() + [_NEW_CHESS])
    if chess in common.CMD_QUIT:
        pass
    elif chess is _NEW_CHESS:
        log.VLOG('insert new chess name')
        name = mio.stdin()
        chess_list.create_chess(name)
        chess = name
    else:
        log.VLOG('choose chess: {}'.format(chess))
    return chess

def process_chess(chess_name):
    if chess_name in common.CMD_QUIT:
        return
    command = mio.choose_command([common.MOD_KEY, _BUILD_TEAM, _RECOMMEND_TEAM])
    if command in common.CMD_QUIT:
        return
    elif command == common.MOD_KEY:
        auto_chess = chess_pieces.ChessPieces(chess_name)
        auto_chess.process_chess()
    elif command == _BUILD_TEAM:
        auto_chess = chess_team.ChessTeam(chess_name)
        auto_chess.build_chess_team()
    elif command == _RECOMMEND_TEAM:
        auto_chess = chess_team.ChessTeam(chess_name)
        auto_chess.recommend_team()

def main():
    chess_name = select_chess()
    process_chess(chess_name)

if __name__ == '__main__':
    main()
