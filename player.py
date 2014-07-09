#!/usr/bin/env python
#encoding: UTF-8

'''
网易云音乐 Player
'''
# Let's make some noise

import subprocess
import threading
import time
import os
import signal
from ui import Ui

# carousel x in [left, right]
carousel = lambda left, right, x: left if (x>right) else (right if x<left else x)


class Player:

    def __init__(self):
        self.popen_handler = None
        # flag stop, prevent thread start
        self.playing_flag = False
        self.pause_flag = False
        self.songs = []
        self.idx = 0

    def popen_recall(self, onExit, popenArgs):
        """
        Runs the given args in a subprocess.Popen, and then calls the function
        onExit when the subprocess completes.
        onExit is a callable object, and popenArgs is a lists/tuple of args that 
        would give to subprocess.Popen.
        """
        def runInThread(onExit, popenArgs):
            self.popen_handler = subprocess.Popen(['mpg123', popenArgs], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.popen_handler.wait()
            if self.playing_flag:
                self.idx = carousel(0, len(self.songs)-1, self.idx+1 )
                onExit()
            return
        thread = threading.Thread(target=runInThread, args=(onExit, popenArgs))
        thread.start()
        # returns immediately after the thread starts
        return thread

    def recall(self):
        self.playing_flag = True
        item = self.songs[ self.idx ]
        Ui().build_playinfo(item['song_name'], item['artist'], item['album_name'])
        self.popen_recall(self.recall, item['mp3_url'])

    def play(self, songs, idx):

        # if same playlists, same song , stop it
        if idx == self.idx and songs == self.songs:
            if self.pause_flag:
                self.resume()
            else:
                self.pause()

        else:
            self.songs = songs
            self.idx = idx

            # if it's playing
            if self.playing_flag:
                self.switch()

            # start new play
            else:
                self.recall()

    # play another   
    def switch(self):
        self.stop()
        # wait process be killed
        time.sleep(1)
        self.recall()

    def stop(self):
        if self.playing_flag:
            self.playing_flag = False
            self.popen_handler.kill()

    def pause(self):
        self.pause_flag = True
        os.kill(self.popen_handler.pid, signal.SIGSTOP)

    def resume(self):
        self.pause_flag = False
        os.kill(self.popen_handler.pid, signal.SIGCONT)

    def next(self):
        self.stop()
        time.sleep(1)
        self.idx = carousel(0, len(self.songs)-1, self.idx+1 )
        self.recall()    

    def prev(self):
        self.stop()
        time.sleep(1)
        self.idx = carousel(0, len(self.songs)-1, self.idx-1 )
        self.recall()
