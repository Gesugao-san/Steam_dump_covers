#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from urllib.error import URLError, HTTPError
import json
import os
import urllib.request
import vdf
from steam.steamid import SteamID
from datetime import datetime


base_url = "https://steamcdn-a.akamaihd.net/steam/apps/"
# Library Game...
base_urls = {
	"Header"            : "header.jpg",
	#"Icon"              : "N\A.jpg",         # https://stackoverflow.com/a/24693219/8175291
	"Cover (1x)"        : "library_600x900.jpg",
	#"Cover (2x)"        : "/library_600x900_2x.jpg", # not used
	"Page BG"           : "library_hero.jpg",
	"Page BG (Blured)"  : "library_hero_blur.jpg",
	"Logo (transparent)": "logo.png",
}

print("Hi")

if not os.path.isfile("data/settings.json"):
	raise SystemExit("no settings file")

with open("data/settings.json", "r", encoding='utf-8') as settings_data_f:
	settings = json.load(settings_data_f)
	#settings_data_f.close()

if not "path_steam_core" in settings:
	raise SystemExit("no \"path_steam_core\" param in settings file")

if not "path_output" in settings:
	raise SystemExit("no \"path_output\" param in settings file")

if not os.path.exists(settings["path_steam_core"]):
	raise SystemExit("no path_steam_core folder founded (check settings file)")

if not os.path.exists(settings["path_output"]):
	raise SystemExit("no path_output folder founded (check settings file)")

print("path_output:", settings["path_steam_core"])
print("path_output:", settings["path_output"])

with open(settings["path_steam_core"] + "/config/loginusers.vdf", "r", encoding='utf-8') as vdf_text:
	loginusers = vdf.parse(vdf_text)
	#input_data_f.close()

if not "users" in loginusers:
	raise SystemExit("no \"loginusers\" param in \"<Steam>/config/loginusers.vdf\" file")

if len(loginusers["users"].keys()) != 1:
	raise SystemExit("Wrong \"users\" length, check file \"<Steam>/config/loginusers.vdf\"")

#print("loginusers:", vdf.dumps(loginusers, pretty=True))
user_SteamID = SteamID(list(loginusers["users"].keys())[0])
print("SteamID:", user_SteamID.as_64, user_SteamID.account_id)

tmp_path = settings["path_steam_core"] + "/userdata/" + str(user_SteamID.account_id) + "/config/localconfig.vdf"
print("tmp_path:", tmp_path)
with open(tmp_path, "r", encoding='utf-8') as vdf_text:
	localconfig = vdf.parse(vdf_text)
	#input_data_f.close()

#print("localconfig:", localconfig)
avatar_hash = localconfig["UserLocalConfigStore"]["friends"][str(user_SteamID.account_id)]["avatar"]
print("localconfig (avatar):", avatar_hash)
print("https://avatars.akamai.steamstatic.com/" + avatar_hash + "_full.jpg")
# "Steam\config\avatarcache"


### USE THIS: http://gaming.stackexchange.com/a/364879/292725 ###
if not os.path.isfile("data/input.json"):
	raise SystemExit("no input file")

with open("data/input.json", "r", encoding='utf-8') as input_data_f:
	input_data = json.load(input_data_f)
	#input_data_f.close()

#print(type(input_data))


#print("App ID:", appid)
longest_gameid = len(str(max(input_data))) #7 # 2290190, for example
longest_base_url = 0
just_len = 0  # justify
for key, value in base_urls.items():
	longest_base_url = len(value)
	check_len = longest_base_url + longest_gameid
	#print('key', key, 'value', value, 'check_len', check_len)
	if just_len < check_len:
		just_len = check_len
just_len -= 2
print('justify len:', just_len)


for appid in input_data:
	for key, value in base_urls.items():
		tmp_url = base_url + str(appid) + "/" + value
		tmp_name = str(appid) + "_" + value
		tmp_file = settings["path_output"] + "\\" + tmp_name
		tmp_exist = os.path.isfile(tmp_file)
		tmp_status1 = str(appid).ljust(longest_gameid + 1) + value.split('.')[0].ljust(longest_base_url - 3)  #'"' + tmp_name + '":'
		print(tmp_status1.ljust(just_len), end='')
		#print(key, '->', value)
		if tmp_exist:
			tmp_status2 = "OK"
			tmp_status3 = "409  Already found" #exists
			print(tmp_status2.ljust(4), tmp_status3)
		else:
			#tmp_status2 = "↓… " #"DOWNLOAD… " #"💾" #"Downloading... "
			#print("File not exist, start downloading...")
			#print(tmp_status2, end='')
			try:
				with urllib.request.urlopen(tmp_url) as f_web:
					f_out = f_web.read() #.decode('utf-8')
					with open(tmp_file, "wb") as fcont:
						fcont.write(f_out)
					tmp_status2 = "OK" #"Downloaded successfully"
					print(tmp_status2)
			except HTTPError as e:
				# "e" can be treated as a http.client.HTTPResponse object
				tmp_status2 = "ERR"
				if e.code == 404:
					tmp_status3 = str(e.code) + "  " + str(e.reason) # remotely # on Steam
				elif e.code == 429:
					tmp_status3 = str(e.code) + "  " + str(e.reason)
					print(tmp_status2.ljust(4), tmp_status3)
					print(str(datetime.now()) + " Stoped bombing Steam.")
					exit()
				else:
					tmp_status3 = "HTTPError:" + str(e.code)
				print(tmp_status2.ljust(4), tmp_status3)
			except URLError as e:
				# https://stackoverflow.com/a/29538780/8175291
				tmp_status2 = "ERR"
				tmp_status3 = "URLError:" + str(e.reason)
				print(tmp_status2.ljust(4), tmp_status3)
			#else:
			#	tmp_status2 = "Downloaded successfully"
			#	print("File \"" + tmp_name + "\" -", tmp_status2)
	#raise SystemExit("ToDo")


print("Bye")
exit()

