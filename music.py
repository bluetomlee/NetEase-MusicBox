#!/usr/bin/env python
#encoding: UTF-8

'''
网易云音乐
'''

import curses
import locale
from api import Api
from player import Player
from ui import Ui
import sys


locale.setlocale(locale.LC_ALL, "")
code = locale.getpreferredencoding()   

keymap = {
    'q': 'quit',
    'j': 'Next',
    'k': 'Previous',
    'h': 'Back',
    'l': 'Forward',
    '[': 'Previous Track',
    ']': 'Next Track',
    'u': 'Previous Page',
    'd': 'Next Page',
    'space': 'stop',
    'enter': 'select'
}

stack = []

# carousel x in [left, right]
carousel = lambda left, right, x: left if (x>right) else (right if x<left else x)

class Menu:
    def __init__(self):
        reload(sys)
        sys.setdefaultencoding('UTF-8')
        self.menus = {
            'title': '网易云音乐Python版',
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
        self.build = 'main'
        self.player = Player()
        self.ui = Ui()
        self.api = Api()
        self.screen = curses.initscr()
        self.screen.keypad(1)

    def menu_ctrl(self):
        key = ''
        self.ui.build_menu(self.menus, self.menu_index, self.build)
        stack.append([self.menus['title'], 'main', 0])
        while key != ord('q'):
            menu_index = self.menu_index
            menus = self.menus
            build = self.build
            idx = menu_index[build]
            key = self.screen.getch()
            self.ui.screen.refresh()
            # Move up
            if key == ord('k'):
                menu_index[build] = carousel(0, len(menus[build])-1, idx-1 )

            # Move down
            elif key == ord('j'):
                menu_index[build] = carousel(0, len(menus[build])-1, idx+1 )

            # Forward, ::curses.KEY_ENTER is unreliable, 10 present <Enter> (mac)
            elif key == ord('\n') or key == ord(' '):
                if build == 'songs':
                    self.player.play(menus['songs'], idx)
                    # prevent rebuild menu swipe playinfo
                    continue

            elif key == ord('l'):
                self.dispatch_enter(idx)

            # Back
            elif key == ord('h'):
                # if not main menu
                if len(stack) == 0:
                    continue
                last = stack.pop()
                self.menus['title'] = last[0] 
                self.build = last[1]
                self.menu_index[self.build] = last[2]

            elif key == ord(']'):
                self.player.next()

            elif key == ord['[']:
                self.player.prev()

            self.ui.build_menu(self.menus, self.menu_index, self.build)

        self.player.stop()
        curses.endwin()

    def dispatch_enter(self, idx):
        # The end of stack
        menus = self.menus
        build = self.build
        menu_index = self.menu_index
        api = self.api
        stack.append( [self.menus['title'], self.build, self.menu_index[self.build]] )

        if build == 'main':
            self.choice_channel(idx)

        elif build == 'artists':
            menu_index['artists'] = 0
            artist_id = menus['artists'][idx]['artist_id']
            data = api.artists(artist_id)
            songs = data['hotSongs']           
            menus['songs'] = api.dig_info(songs, 'songs')
            self.build = 'songs'
            menus['title'] = '艺术家 > ' + menus['artists'][idx]['artists_name']

        elif build == 'albums':
            menu_index['albums'] = 0
            album_id = menus['albums'][idx]['album_id']
            data = api.album(album_id)
            songs = data['album']['songs']
            menus['songs'] = api.dig_info(songs, 'songs')
            self.build = 'songs'
            menus['title'] = '专辑 > ' + menus['albums'][idx]['albums_name']

        elif build == 'playlists':
            menu_index['playlists'] = 0
            playlist_id = menus['playlists'][idx]['playlist_id']
            data = api.playlist_detail(playlist_id)
            songs = data['result']['tracks']
            menus['songs'] = api.dig_info(songs, 'songs')
            self.build = 'songs'
            menus['title'] = '网易精选集 > ' + menus['playlists'][idx]['playlists_name']
    

    def choice_channel(self, idx):
        # song toplist
        api = self.api
        if idx == 0:
            data = api.top_songlist()
            songs = data['songs']
            self.menus['songs'] = api.dig_info(songs, 'songs')
            self.menus['title'] = '排行榜'
            self.build = 'songs'

        # artists toplist, 热门艺术家
        elif idx == 1:
            data = api.top_artists()
            artists = data['artists']
            self.menus['artists'] = api.dig_info(artists, 'artists')
            self.menus['title'] = '艺术家'
            self.build = 'artists'

        # album toplist， 新碟上架
        elif idx == 2:
            data = api.new_albums()
            albums = data['albums']
            self.menus['albums'] = api.dig_info(albums, 'albums')
            self.menus['title'] = '新碟上架'
            self.build = 'albums'

        # playlist toplist， 网易精选碟
        elif idx == 3:
            data = api.top_playlists()
            playlists = data['playlists']
            self.menus['playlists'] = api.dig_info(playlists, 'playlists')
            self.menus['title'] = '网易精选碟'
            self.build = 'playlists'            

        # DJ电台
        elif idx == 4:
            pass

        elif idx == 5 or idx == 6 or idx == 7:
            self.ui.build_search( idx )

        elif idx == 8:
            self.ui.build_login()


Menu().menu_ctrl()
# print api.search('dfsagddf')
