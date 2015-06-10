#!/usr/bin/env python
#encoding: UTF-8
from api import NetEase
from flask import Flask, jsonify, request
import requests
import json

app = Flask(__name__)

@app.route('/music/search/<q>/<limit>')
def search_music(q, limit):
	netease = NetEase()
	r = netease.search(q, limit=limit)
	if r['code'] != 200:
		return jsonify({
			"error"		:	True
			})
	else:
		ids = []
		for song in r['result']['songs']:
			ids.append(song['id'])
		musics = netease.songs_detail(ids)
		outputs = []
		for music in musics:
			outputs.append({
				"error"	:	False,
				"name"	:	music['name'],
				"cover"	:	music['album']['blurPicUrl'],
				"album_name":	music['album']['name'],
				"author": 	music['artists'][0]['name'],
				"url"	:	music['mp3Url']
				})
		outputs = {
			"error"		:	False,
			"type"		:	"music",
			"musics"	:	outputs
		}
		return jsonify(outputs)

@app.route('/music/search', methods=['POST'])
def search():
	q = request.form['content']
	return search_music(q, 1)
	
@app.route("/weather/<location>")
def weather(location):
	url = "http://api.map.baidu.com/telematics/v3/weather?location=%s&output=json&ak=65VSjZ1CEe8lnb5q3XGzlCUc"%location
	print url
	r = requests.get(url)
	r = r.json()
	if r['error'] != 0:
		return jsonify({
			"error"	:	True
			})
	else:
		return json.dumps({
			"error"		:	False,
			"weathers"	:	r["results"][0]['weather_data']
			})

@app.route('/weather', methods=['POST'])
def check_weather():
	location = request.form['content']
	return weather(location)

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=80,debug=True)