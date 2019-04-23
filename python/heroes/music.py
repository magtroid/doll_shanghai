#!/usr/bin/env python
# coding=utf-8

'''
music class
Magtroid @ 2019-04-19 14:16
'''

import hero_config
import common
import datalib
import log
import mio
# import threadpoolmanager
import processingpoolmanager
import tools

_MUSIC_KEY = 'music'
_MUSIC_PLAY_KEY = 'play'
_MUSIC_NAME_KEY = 'name'
_MUSIC_PATH_KEY = 'path'
_NEW_MUSIC = '_new_music'

class Music(object):
    '''
    public:
      get_music_list
      insert_music
      play
      stop
    private:
      __write_data_lib
    '''

    def __init__(self, schedule = False):
        self.__music_data_path = tools.join_path([hero_config.DATALIB, _MUSIC_KEY + '.lib'])
        self.__disable_controler = True
        self.__music_lib = datalib.DataLib(self.__music_data_path, self.__disable_controler)
        self.__music_lib.load_data_lib(schedule = schedule)

    def get_music_list(self):
        return list(self.__music_lib.get_data().keys())

    def insert_music(self):
        while True:
            log.INFO('please insert music name')
            music_name = mio.stdin()
            if music_name in common.CMD_QUIT:
                break
            log.INFO('please choose music from resource')
            music_path = tools.choose_file_from_dir(hero_config.MUSICLIB)
            if music_name in common.CMD_QUIT:
                break
            new_music = dict()
            new_music[_MUSIC_NAME_KEY] = music_name
            new_music[_MUSIC_PATH_KEY] = music_path
            log.INFO('insert music: {}'.format(music_name))
            self.__music_lib.insert_data(common.EMPTY_KEY, new_music, _MUSIC_NAME_KEY)
        save_or_not = mio.choose_command(common.YON_COMMAND)
        if save_or_not is common.Y_COMMAND:
            self.__write_data_lib()

    def play(self, music_name):
        data = self.__music_lib.get_data()
        if music_name not in data:
            log.VLOG('music: {} not exist'.format(music_name))
            return
        music_path = tools.join_path([hero_config.MUSICLIB, data[music_name][_MUSIC_PATH_KEY]])
        tools.play_music(music_path)

    def stop(self):
        tools.stop_processing(command = _MUSIC_PLAY_KEY)

    def __write_data_lib(self):
        self.__music_lib.write_data_lib()

music_manager = Music()
processingpoolmanager.new_processing(1, name = _MUSIC_KEY)

def get_music_list():
    return music_manager.get_music_list()

def play(music_name):
    processingpoolmanager.put_request(music_manager.play, args = [music_name], name = _MUSIC_KEY)

def stop():
    processingpoolmanager.dismiss_processing(name = _MUSIC_KEY)
    music_manager.stop()

def main():
    log.VLOG('choose a music to play')
    while True:
        command = mio.choose_command(get_music_list() + [_NEW_MUSIC])
        if command in common.CMD_QUIT:
            stop()
            break
        elif command == _NEW_MUSIC:
            music_manager.insert_music()
        else:
            play(command)

if __name__ == '__main__':
    main()
