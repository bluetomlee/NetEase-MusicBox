#!/usr/bin/env python
#encoding: UTF-8

'''
网易云音乐
'''

import curses
import locale
from api import Api
import time
import sys

locale.setlocale(locale.LC_ALL, "")
code = locale.getpreferredencoding()   


class Menu:
    def __init__(self):
        self.screen = curses.initscr()
        # charactor break buffer
        curses.cbreak()
        self.screen.keypad(1)
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        self.menus = {
            'title': '欢迎使用网易云音乐Python版 当前版本v1.0',
            'curr': 'main',
            'main': ['排行榜', '艺术家', '新碟上架', '网易精选碟', 'DJ电台', '搜索音乐', '搜索艺术家', '搜索专辑', '登录'],
            'songs': [],
            'artists': [],
            'albums': [],
            'playlists': []
        }
        self.menu_index = {
            'main': 0,
            'songs': 0,
            'artists': 0,
            'albums': 0,
            'playlists': 0
        }

        self.stack = [[0,],]

        self.build = 'main'
        reload(sys)
        sys.setdefaultencoding('UTF-8')

    def build_menu(self):
        self.screen.clear()
        self.screen.addstr(4, 19, self.menus['title'], curses.color_pair(1))
        if len(self.menus[self.build]) == 0:
            self.screen.addstr(8, 19, '未找到搜索结果 -，-')

        else:
            if self.build == 'main':
                for i in range( 0, len(self.menus['main']) ):
                    if i == self.menu_index['main']:
                        self.screen.addstr(i+8, 16, '>> ' + self.menus['main'][i], curses.color_pair(2))
                    else:
                        self.screen.addstr(i+8, 19, self.menus['main'][i])

            elif self.build == 'songs':
                for i in range(0, len(self.menus['songs'])):
                    if i == self.menu_index['songs']:
                        self.screen.addstr(i+8, 16, '>> ' + self.menus['songs'][i]['song_name'] + '   -   ' + self.menus['songs'][i]['artist'], curses.color_pair(2))
                    else:
                        self.screen.addstr(i+8, 19, self.menus['songs'][i]['song_name'] + '   -   ' + self.menus['songs'][i]['artist'])
            
            elif self.build == 'artists':
                for i in range(0, len(self.menus['artists'])):
                    if i == self.menu_index['artists']:
                        self.screen.addstr(i+8, 16, '>> ' + self.menus['artists'][i]['artists_name'] + '   -   ' + str(self.menus['artists'][i]['alias']), curses.color_pair(2))
                    else:
                        self.screen.addstr(i+8, 19, self.menus['artists'][i]['artists_name'] + '   -   ' + self.menus['artists'][i]['alias'])

            elif self.build == 'albums':
                for i in range(0, len(self.menus['albums'])):
                    if i == self.menu_index['albums']:
                        self.screen.addstr(i+8, 16, '>> ' + self.menus['albums'][i]['albums_name'] + '   -   ' + self.menus['albums'][i]['artists_name'], curses.color_pair(2))
                    else:
                        self.screen.addstr(i+8, 19, self.menus['albums'][i]['albums_name'] + '   -   ' + self.menus['albums'][i]['artists_name'])

            elif self.build == 'playlists':
                for i in range(0, len(self.menus['playlists'])):
                    if i == self.menu_index['playlists']:
                        self.screen.addstr(i+8, 16, '>> ' + self.menus['playlists'][i]['playlists_name'] + '   -   ' + self.menus['playlists'][i]['creator_name'], curses.color_pair(2))
                    else:
                        self.screen.addstr(i+8, 19, self.menus['playlists'][i]['playlists_name'] + '   -   ' + self.menus['playlists'][i]['creator_name'])

        self.screen.refresh()

    def get_param(self, prompt_string):
        self.screen.clear()
        self.screen.border(0)
        self.screen.addstr(2, 2, prompt_string)
        self.screen.refresh()
        input = self.screen.getstr(10, 10, 60)
        if input.strip() is '':
            return self.get_param(prompt_string)
        else:
            return input

    def build_search(self, stype):
        if stype == 5:
            song_name = self.get_param('搜索歌曲：')
            data = Api().search(song_name, stype=1)
            song_ids = []
            if 'songs' in data['result']:
                if 'mp3Url' in data['result']['songs']:
                    songs = data['result']['songs']

                # search song result do not has mp3Url
                # send ids to get mp3Url
                else:
                    for i in range(0, len(data['result']['songs']) ):
                        song_ids.append( data['result']['songs'][i]['id'] )
                    data = Api().songs_detail(song_ids)
                    songs = data['songs']

                self.dig_info(songs, 'songs')
            else:
                self.menus['songs'] = []

            self.build = 'songs'
        
        elif stype == 6:
            artist_name = self.get_param('搜索艺术家：')
            data = Api().search(artist_name, stype=100)
            if 'artists' in data['result']:
                artists = data['result']['artists']
                self.dig_info(artists, 'artists')
            else:
                self.menus['artists'] = []

            self.build = 'artists'

        elif stype == 7:
            artist_name = self.get_param('搜索专辑：')
            data = Api().search(artist_name, stype=10)
            if 'albums' in data['result']:
                albums = data['result']['albums']
                self.dig_info(albums, 'albums')
            else:
                self.menus['albums'] = []
            self.build = 'albums'

        self.build_menu()

    def dig_info(self, data, jtype):
        if jtype == 'songs':
            self.menus['songs'] = []
            for i in range(0, min(10, len(data) ) ):
                song_info = {
                    'song_id': data[i]['id'],
                    'artist': [],
                    'song_name': data[i]['name'],
                    'mp3_url': data[i]['mp3Url']   
                }
                if 'artist' in data[i]:
                    song_info['artist'] = data[i]['artist']
                elif 'artists' in data[i]:
                    for j in range(0, len(data[i]['artists']) ):
                        song_info['artist'].append( data[i]['artists'][j]['name'] )
                    song_info['artist'] = ', '.join( song_info['artist'] )
                else:
                    song_info['artist'] = '未知艺术家'

                self.menus['songs'].append(song_info)

        if jtype == 'artists':
            self.menus['artists'] = []
            for i in range(0, min(10, len(data) ) ):
                artists_info = {
                    'artist_id': data[i]['id'],
                    'artists_name': data[i]['name'],
                    'alias': ''.join(data[i]['alias'])
                }
                self.menus['artists'].append(artists_info)

        if jtype == 'albums':
            self.menus['albums'] = []
            for i in range(0, min(10, len(data) ) ):
                albums_info = {
                    'album_id': data[i]['id'],
                    'albums_name': data[i]['name'],
                    'artists_name': data[i]['artist']['name']
                }
                self.menus['albums'].append(albums_info)

        if jtype == 'playlists':
            self.menus['playlists'] = []
            for i in range(0, min(10, len(data) ) ):
                playlists_info = {
                    'playlist_id': data[i]['id'],
                    'playlists_name': data[i]['name'],
                    'creator_name': data[i]['creator']['nickname']
                }
                self.menus['playlists'].append(playlists_info)

    def menu_ctrl(self):
        key = ''
        self.build_menu()
        # carousel x in [left, right]
        carousel = lambda left, right, x: left if (x>right) else (right if x<left else x)
        while key != ord('q'):
            idx = self.menu_index[self.build]
            key = self.screen.getch()
            self.screen.refresh()
            if key == curses.KEY_UP:
                self.menu_index[self.build] = carousel(0, len(self.menus[self.build])-1, idx-1 )

            elif key == curses.KEY_DOWN:
                self.menu_index[self.build] = carousel(0, len(self.menus[self.build])-1, idx+1 )

            # Forward, ::curses.KEY_ENTER is unreliable, 10 present <Enter> (mac)
            elif key == 10:
                self.stack.append( [self.menus['title'], self.build, self.menu_index] )
                self.menus['title'] = self.menus['main'][idx]
                if self.build == 'main':
                    self.main_move(idx)

                elif self.build == 'artists':
                    self.menu_index['artists'] = 0
                    artist_id = self.menus['artists'][idx]['artist_id']
                    data = Api().artists(artist_id)
                    songs = data['hotSongs']
                    self.dig_info(songs, 'songs')
                    self.build = 'songs'
                    self.menus['title'] = '艺术家 > ' + self.menus['artists'][idx]['artists_name']

                elif self.build == 'albums':
                    album_id = self.menus['albums'][idx]['album_id']
                    data = Api().album(album_id)
                    songs = data['album']['songs']
                    self.dig_info(songs, 'songs')
                    self.build = 'songs'
                    self.menus['title'] = '专辑 > ' + self.menus['albums'][idx]['albums_name']

                elif self.build == 'playlists':
                    playlist_id = self.menus['playlists'][idx]['playlist_id']
                    data = Api().playlist_detail(playlist_id)
                    songs = data['result']['tracks']
                    self.dig_info(songs, 'songs')
                    self.build = 'songs'
                    self.menus['title'] = '网易精选集 > ' + self.menus['playlists'][idx]['playlists_name']

                elif self.build == 'songs':
                    mp3_url = self.menus['songs'][idx]['mp3_url']
                    Player().play(mp3_url)


            # Back
            elif key == curses.KEY_LEFT:
                # main menu, no more back
                if len(self.stack) != 1:
                    last = self.stack.pop()
                    self.menus['title'] = last[0] 
                    self.build = last[1]
                    self.menu_index = last[2]

            self.build_menu()

        curses.endwin()

    def main_move(self, idx):
        # song toplist
        if idx == 0:
            data = Api().top_songlist()
            songs = data['songs']
            self.dig_info(songs, 'songs')
            self.build = 'songs'

        # artists toplist, 热门艺术家
        elif idx == 1:
            data = Api().top_artists()
            artists = data['artists']
            self.dig_info(artists, 'artists')
            self.build = 'artists'

        # album toplist， 新碟上架
        elif idx == 2:
            data = Api().new_albums()
            albums = data['albums']
            self.dig_info(albums, 'albums')
            self.build = 'albums'

        # playlist toplist， 网易精选碟
        elif idx == 3:
            data = Api().top_playlists()
            playlists = data['playlists']
            self.dig_info(playlists, 'playlists')
            self.build = 'playlists'            

        # DJ电台
        elif idx == 4:
            pass

        elif idx == 5 or idx == 6 or idx == 7:
            self.build_search( idx )

        elif idx == 8:
            self.build_login()

# class Player:

Menu().menu_ctrl()
# print Api().search('dfsagddf')
