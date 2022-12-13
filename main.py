#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import json
import urllib.request
from urllib.error import URLError, HTTPError
import os


base_url = "https://steamcdn-a.akamaihd.net/steam/apps/"
# Library Game...
base_urls = {
	"Header"            : "header.jpg",
	#"Icon"              : "N\A.jpg",                 # https:    //stackoverflow.com/a/24693219/8175291
	"Cover (1x)"        : "library_600x900.jpg",
	#"Cover (2x)"        : "/library_600x900_2x.jpg", # not used
	"Page BG"           : "library_hero.jpg",
	"Page BG (Blured)"  : "library_hero_blur.jpg",
	"Logo (transparent)": "logo.png",
}

print("Hi")

if not os.path.isfile("data/settings.json"):
	raise SystemExit("no settings file")

with open("data/settings.json", "r") as settings_data_f:
	settings = json.load(settings_data_f)
	#settings_data_f.close()

if not "path_output" in settings:
	raise SystemExit("no \"path_output\" param in settings file")

if not os.path.exists(settings["path_output"]):
	raise SystemExit("no output folder founded (check settings file)")

print("path_output:", settings["path_output"])

### USE THIS: http://gaming.stackexchange.com/a/364879/292725 ###
if not os.path.isfile("data/input.json"):
	raise SystemExit("no input file")

with open("data/input.json", "r") as input_data_f:
	input_data = json.load(input_data_f)
	#input_data_f.close()

print(type(input_data))


for appid in input_data:
	#print("App ID:", appid)
	for key, value in base_urls.items():
		tmp_url = base_url + str(appid) + "/" + value
		tmp_name = str(appid) + "_" + value
		tmp_file = settings["path_output"] + "\\" + tmp_name
		tmp_exist = os.path.isfile(tmp_file)
		#print(key, '->', value)
		if not tmp_exist:
			tmp_status = "Not present, downloading..."
			#print("File not exist, start downloading...")
			try:
				with urllib.request.urlopen(tmp_url) as f_web:
					f_out = f_web.read() #.decode('utf-8')
					with open(tmp_file, "wb") as fcont:
						fcont.write(f_out)
					tmp_status = "Downloaded successfully"
					print("File \"" + tmp_name + "\" -", tmp_status)
			except HTTPError as e:
				# "e" can be treated as a http.client.HTTPResponse object
				if e.code == 404:
					tmp_status = "Not presented on server, skipping"
				else:
					tmp_status = "HTTPError:" + e.code + ", skipping"
				print("File \"" + tmp_name + "\" -", tmp_status)
			except URLError as e:
				# https://stackoverflow.com/a/29538780/8175291
				tmp_status = "URLError:" + e.reason + ", skipping"
				print("File \"" + tmp_name + "\" -", tmp_status)
			#else:
			#	tmp_status = "Downloaded successfully"
			#	print("File \"" + tmp_name + "\" -", tmp_status)
		else:
			tmp_status = "Presented locally, skipping"
			print("File \"" + tmp_name + "\" -", tmp_status)
	#raise SystemExit("ToDo")


print("Bye")

