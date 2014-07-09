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
    'f': 'Search',
    'space': 'Play/Pause',
    'enter': 'select'
}

# stack = [ [ datatype, title, datalist, offset, index ], [ ] ]
stack = []
step = 10

# carousel x in [left, right]
carousel = lambda left, right, x: left if (x>right) else (right if x<left else x)

class Menu:
    def __init__(self):
        reload(sys)
        sys.setdefaultencoding('UTF-8')
        self.datatype = 'main'
        self.title = '网易云音乐Python版'
        self.datalist = ['排行榜', '艺术家', '新碟上架', '网易精选碟', 'DJ电台', '搜索', '登录']
        self.offset = 0
        self.index = 0
        self.player = Player()
        self.ui = Ui()
        self.api = Api()
        self.screen = curses.initscr()
        self.screen.keypad(1)

    def menu_ctrl(self):
        key = ''
        self.ui.build_menu(self.datatype, self.title, self.datalist, self.offset, self.index, step)
        stack.append([self.datatype, self.title, self.datalist, self.offset, self.index])
        while key != ord('q'):
            datatype = self.datatype
            datalist = self.datalist
            offset = self.offset
            idx = index = self.index
            key = self.screen.getch()
            self.ui.screen.refresh()
            # Move up
            if key == ord('k'):
                self.index = carousel(offset, min( len(datalist), offset + step) - 1, idx-1 )

            # Move down
            elif key == ord('j'):
                self.index = carousel(offset, min( len(datalist), offset + step) - 1, idx+1 )

            # Page up
            elif key == ord('u'):
                if offset == 0:
                    continue
                self.offset -= step

                # e.g. 23 - 10 = 13 --> 10
                self.index = (index-step)//step*step

            # Page down
            elif key == ord('d'):
                if offset + step >= len( datalist ):
                    continue
                self.offset += step

                # e.g. 23 + 10 = 33 --> 30
                self.index = (index+step)//step*step

            # Forward, ::curses.KEY_ENTER is unreliable, 10 present <Enter> (mac)
            elif key == ord(' '):
                if datatype == 'songs':
                    self.player.play(datalist, idx)
                    # prevent redatatype menu swipe playinfo
                    # continue
            elif key == ord('o'):
                self.player.pause()

            elif key == ord('\n'):
                self.player.resume()

            elif key == ord('l'):
                if self.datatype == 'songs':
                    continue
                self.dispatch_enter(idx)
                self.index = 0
                self.offset = 0    

            # Back
            elif key == ord('h'):
                # if not main menu
                if self.datatype == 'main':
                    continue
                up = stack.pop()
                self.datatype = up[0]
                self.title = up[1]
                self.datalist = up[2]
                self.offset = up[3]
                self.index = up[4]

            elif key == ord('f'):
                self.search()


            elif key == ord(']'):
                self.player.next()

            elif key == ord('['):
                self.player.prev()

            self.ui.build_menu(self.datatype, self.title, self.datalist, self.offset, self.index, step)

        self.player.stop()
        curses.endwin()

    def dispatch_enter(self, idx):
        # The end of stack
        api = self.api
        datatype = self.datatype
        title = self.title
        datalist = self.datalist
        offset = self.offset
        index = self.index
        stack.append( [datatype, title, datalist, offset, index])

        if datatype == 'main':
            self.choice_channel(idx)
            return

        # 该艺术家的热门歌曲
        elif datatype == 'artists':
            artist_id = datalist[idx]['artist_id']
            data = api.artists(artist_id)
            songs = data['hotSongs']           
            self.datatype = 'songs'
            self.datalist = api.dig_info(songs, 'songs')
            self.title = '艺术家 > ' + datalist[idx]['artists_name']

        # 该专辑包含的歌曲
        elif datatype == 'albums':
            album_id = datalist[idx]['album_id']
            data = api.album(album_id)
            songs = data['album']['songs']
            self.datatype = 'songs'
            self.datalist = api.dig_info(songs, 'songs')
            self.title = '专辑 > ' + datalist[idx]['albums_name']

        # 该歌单包含的歌曲
        elif datatype == 'playlists':
            playlist_id = datalist[idx]['playlist_id']
            data = api.playlist_detail(playlist_id)
            songs = data['result']['tracks']
            self.datatype = 'songs'
            self.datalist = api.dig_info(songs, 'songs')
            self.title = '网易精选集 > ' + datalist[idx]['playlists_name']

    def choice_channel(self, idx):
        # song toplist
        api = self.api
        if idx == 0:
            data = api.top_songlist()
            songs = data['songs']
            self.datalist = api.dig_info(songs, 'songs')
            self.title = '排行榜'
            self.datatype = 'songs'

        # artists toplist, 热门艺术家
        elif idx == 1:
            data = api.top_artists()
            artists = data['artists']
            self.datalist = api.dig_info(artists, 'artists')
            self.title = '艺术家'
            self.datatype = 'artists'

        # album toplist， 新碟上架
        elif idx == 2:
            data = api.new_albums()
            albums = data['albums']
            self.datalist = api.dig_info(albums, 'albums')
            self.title = '新碟上架'
            self.datatype = 'albums'

        # playlist toplist， 网易精选碟
        elif idx == 3:
            data = api.top_playlists()
            playlists = data['playlists']
            self.datalist = api.dig_info(playlists, 'playlists')
            self.title = '网易精选碟'
            self.datatype = 'playlists'            

        # DJ电台
        elif idx == 4:
            pass

        elif idx == 5:
            self.search()

        elif idx == 6:
            self.ui.build_login()

    def search(self):
        ui = self.ui
        x = ui.build_search_menu()
        if x in range(ord('1'), ord('5')):
            # if really do search, push current info into stack
            stack.append( [self.datatype, self.title, self.datalist, self.offset, self.index ])
            self.index = 0
            self.offset = 0

        if x == ord('1'):
            self.datatype = 'songs'
            self.datalist = ui.build_search('songs')
            self.title = '歌曲搜索结果:'

        elif x == ord('2'):
            self.datatype = 'artists'
            self.datalist = ui.build_search('artists')
            self.title = '艺术家搜索结果:'

        elif x == ord('3'):
            self.datatype = 'albums'
            self.datalist = ui.build_search('albums')
            self.title = '专辑搜索结果:'

        elif x == ord('4'):
            self.datatype = 'playlists'
            self.datalist = ui.build_search('playlists')
            self.title = '网易精选集搜索结果:'

        # elif x == ord('5'):
        #     self.datatype = 'users'
        #     self.datalist = ui.build_search('users')
        #     self.title = '用户搜索结果:'


Menu().menu_ctrl()
# print api.search('dfsagddf')
