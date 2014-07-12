#!/usr/bin/env python
# encoding: UTF-8
'''
豆瓣FM Api
'''

import re
import json
import requests


class Douban:

    def __init__(self):
        self.header = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'http://www.douban.com/'
        }
        self.data = {
            'app_name': 'radio_desktop_win',
            'version': 100,
            'email': 'seaplor@hotmail.com',
            'password': 'zs8MHRcvwGdG4k'
        }    
        self.user = {}
        self.channels = []
        # self.user = self.httpRequest('POST', 'http://www.douban.com/j/app/login', self.data)

    def httpRequest(self, method, action, query=None, urlencoded=None, callback=None, timeout=None):
        try:
            if(method == 'GET'):
                url = action if (query == None) else (action + '?' + query)
                connection = requests.get(url, headers=self.header, timeout=5)

            elif(method == 'POST'):
                connection = requests.post(
                    action,
                    data=query,
                    headers=self.header,
                    timeout=5
                )
                connection.encoding = "UTF-8"

        except requests.exceptions.Timeout:
            print('Request Time Out, Please Try Later...')

        except requests.exceptions.ConnectionError:
            print('Invalid Connection')

        else:
            connection.encoding = "UTF-8"
            connection = json.loads(connection.text)
            return connection

    def login(self):
        self.user = self.httpRequest('POST', 'http://www.douban.com/j/app/login', self.data)

    def get_channels(self):
        data = self.httpRequest('GET', 'http://www.douban.com/j/app/radio/channels')
        self.channels = data['channels']
        return self.channels

    def get_songs(self, channel_id, stype):
        action = 'http://www.douban.com/j/app/radio/people?app_name=radio_desktop_win&version=100&channel=' + str(channel_id) + '&type=' + stype
        data = self.httpRequest('GET', action)
        self.songs = self.dig_info( data['song'] )
        return self.songs

    def dig_info(self, data):
        temp = []
        for i in range(0, len(data) ):
            song_info = {
                'song_id': data[i]['sid'],
                'artist': data[i]['artist'],
                'song_name': data[i]['title'],
                'album_name': data[i]['albumtitle'],
                'mp3_url': data[i]['url']
            }
            temp.append(song_info)
        return temp        










