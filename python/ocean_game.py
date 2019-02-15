#!/usr/bin/env python
# coding=utf-8

import random
import sys
import tools

_MAX_TIME = 3
_PLAYER_NUMBER = 5
_FIRST_GAME_NUMBER = 10000
_SECOND_GAME_NUMBER = 100000
_BATTLE_RATIO = 0.5  # the bigger means the stronger of our team
_WIN = 'win'
_LOSE = 'lose'
_TOP_NUMBER = 10

def list2str(alist):
    return ' '.join(list(map(str, alist)))

def str2list(astr):
    return list(map(int, astr.split()))

def generate_team(team_member):
    if len(team_member) == 1:
        return [team_member]
    teams = []
    for i in range(len(team_member)):
        left_member = team_member[:]
        del left_member[i]
        teams += [[team_member[i]] + x for x in generate_team(left_member)]
    return teams

def battle(ocean_team, opponent):
    player_a = 0
    player_b = 0
    times_a = 0
    times_b = 0
    while player_a < _PLAYER_NUMBER and player_b < _PLAYER_NUMBER:
        if ocean_team[player_a] < opponent[player_b]:
            player_b += 1
            times_a += 1
            times_b = 0
        elif ocean_team[player_a] > opponent[player_b]:
            player_a += 1
            times_a = 0
            times_b += 1
        else:
            if random.random() < _BATTLE_RATIO:
                player_b += 1
                times_a += 1
                times_b = 0
            else:
                player_a += 1
                times_a = 0
                times_b += 1
        if player_a >= _PLAYER_NUMBER or player_b >= _PLAYER_NUMBER:
            break
        if times_a == _MAX_TIME:
            player_a += 1
            times_a = 0
        if times_b == _MAX_TIME:
            player_b += 1
            times_b = 0
    if player_a == _PLAYER_NUMBER:
        return _LOSE
    else:
        return _WIN

def ocean_game(ocean_team, ocean_teams, game_number):
    result = {_WIN : 0, _LOSE : 0}
    for i in range(game_number):
        opponent = ocean_teams[int(len(ocean_teams) * random.random())]
        result[battle(ocean_team, opponent)] += 1
    return result

def main(argv):
    print('generate ocean team')
    team_member = [x + 1 for x in range(_PLAYER_NUMBER)]
    ocean_teams = generate_team(team_member)

    print('begin to first select team')
    ocean_result = dict()
    for i in range(len(ocean_teams)):
        ocean_team = ocean_teams[i]
        tools.schedule(i + 1, len(ocean_teams))
        ocean_result[list2str(ocean_team)] = ocean_game(ocean_team, ocean_teams, _FIRST_GAME_NUMBER)

    print('begin to first rank')
    top_n = 0
    top_ocean_teams = []
    for item in sorted(ocean_result.items(), key = lambda d:d[1][_WIN], reverse=True):
        print('{:20s} {:10d} {:10d} {:10.2f}'.format(item[0], item[1][_WIN], item[1][_LOSE], float(item[1][_WIN]) / _FIRST_GAME_NUMBER * 100))
        top_ocean_teams.append(str2list(item[0]))
        top_n += 1
        if top_n >= _TOP_NUMBER:
            break

    print('begin to second select team')
    top_ocean_result = dict()
    for i in range(len(top_ocean_teams)):
        top_ocean_team = top_ocean_teams[i]
        tools.schedule(i + 1, len(top_ocean_teams))
        top_ocean_result[list2str(top_ocean_team)] = ocean_game(top_ocean_team, top_ocean_teams, _SECOND_GAME_NUMBER)

    print('begin to second rank')
    for item in sorted(top_ocean_result.items(), key = lambda d:d[1][_WIN], reverse=True):
        print('{:20s} {:10d} {:10d} {:10.2f}'.format(item[0], item[1][_WIN], item[1][_LOSE], float(item[1][_WIN]) / _SECOND_GAME_NUMBER * 100))

if __name__ == '__main__':
    main(sys.argv)
