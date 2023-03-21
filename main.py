#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from datetime import datetime
from steam.steamid import SteamID
from urllib.error import URLError, HTTPError
import json
import os
import signal
import sys
import urllib.request
import vdf


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

def save_presence_db(_presence_data):
	print("Saving \"data/presence_db.json\" file... ", end='')
	with open("data/presence_db.json", "w", encoding='utf-8') as presence_db_file:
		presence_db_file.write(json.dumps(_presence_data, indent=2) + "\n")
		presence_db_file.close()
	print("done.")

if not os.path.isfile("data/presence_db.json"):
	print("No \"data/presence_db.json\" file, creating...")
	save_presence_db({})
	presence_data_persistent = {}
else:
	with open("data/presence_db.json", "r", encoding='utf-8') as presence_db_file:
		presence_data_persistent = json.load(presence_db_file)
		presence_db_file.close()


if not os.path.isfile("data/settings.json"):
	raise SystemExit("no settings file")
else:
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


#print("App ID:", appid_str)
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
max_missing_data = len(base_urls.keys())
print('justify len:', just_len, "max_missing_data:", max_missing_data)

# https://stackoverflow.com/a/1112350/8175291
def signal_handler(sig, frame):
	print("\n")
	print("presence_data_persistent:", presence_data_persistent)
	print('You pressed Ctrl-C!')
	#sys.exit(0)
	save_presence_db(presence_data_persistent)
	exit()

signal.signal(signal.SIGINT, signal_handler)
#print('Press Ctrl+C')
#signal.pause()


for appid_int in input_data:
	appid_str = str(appid_int)
	presence_data_persistent = presence_data_persistent
	presence_data_temp = {appid_str: {}}
	presence_missing_count = 0
	for surl_name, surl in base_urls.items():
		url_index = list(base_urls.values()).index(surl) + 1 #surl_name
		tmp_url = base_url + appid_str + "/" + surl
		tmp_name = appid_str + "_" + surl
		tmp_file = settings["path_output"] + "\\" + tmp_name
		tmp_exist = os.path.isfile(tmp_file)
		tmp_status1 = appid_str.ljust(longest_gameid + 1) + surl.split('.')[0].ljust(longest_base_url - 3)  #'"' + tmp_name + '":'
		print(tmp_status1.ljust(just_len), end='')
		#print(key, '->', value)
		if tmp_exist:
			tmp_status2 = "OK"
			tmp_status3 = "409 Already found" #exists
			if presence_data_persistent.get(appid_str) != None:
				presence_data_persistent[appid_str].update({url_index: True})
			else:
				presence_data_persistent[appid_str] = {url_index: True}
			print(tmp_status2.ljust(3), tmp_status3)
		else:
			#tmp_status2 = "↓… " #"DOWNLOAD… " #"💾" #"Downloading... "
			#print("File not exist, start downloading...")
			#print(tmp_status2, end='')
			try:
				with urllib.request.urlopen(tmp_url) as f_web:
					f_out = f_web.read() #.decode('utf-8')
					with open(tmp_file, "wb") as fcont:
						fcont.write(f_out)
					tmp_status2 = "OK 200" #"Downloaded successfully"
					print(tmp_status2)
					if presence_data_persistent.get(appid_str) != None:
						presence_data_persistent[appid_str].update({url_index: True})
					else:
						presence_data_persistent[appid_str] = {url_index: True}
					save_presence_db(presence_data_persistent)
			except HTTPError as e:
				# "e" can be treated as a http.client.HTTPResponse object
				tmp_status2 = "ERR"
				if e.code == 404:
					tmp_status3 = str(e.code) + " " + str(e.reason) # remotely # on Steam
					if presence_data_persistent.get(appid_str) != None:
						presence_data_persistent[appid_str].update({url_index: e.code})
					else:
						presence_data_persistent[appid_str] = {url_index: e.code}
					presence_missing_count += 1
				elif e.code == 429:
					tmp_status3 = str(e.code) + " " + str(e.reason)
					if presence_data_persistent.get(appid_str) != None:
						presence_data_persistent[appid_str].update({url_index: e.code})
					else:
						presence_data_persistent[appid_str] = {url_index: e.code}
					print(tmp_status2.ljust(3), tmp_status3)
					print(str(datetime.now()) + " Stoped bombing Steam.")
					presence_missing_count += 1

					save_presence_db(presence_data_persistent)
					exit()
				else:
					presence_missing_count += 1
					tmp_status3 = "HTTPError:" + str(e.code)
				print(tmp_status2.ljust(3), tmp_status3)
			except URLError as e:
				# https://stackoverflow.com/a/29538780/8175291
				tmp_status2 = "ERR"
				tmp_status3 = "URLError:" + str(e.reason)
				print(tmp_status2.ljust(3), tmp_status3)
				if presence_data_persistent.get(appid_str) != None:
					presence_data_persistent[appid_str].update({url_index: str(e)})
				else:
					presence_data_persistent[appid_str] = {url_index: str(e)}
				presence_missing_count += 1
			#else:
			#	tmp_status2 = "Downloaded successfully"
			#	print("File \"" + tmp_name + "\" -", tmp_status2)
	save_presence_db(presence_data_persistent)
	#raise SystemExit("ToDo")


print("Bye")
exit()

