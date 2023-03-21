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
	"0. Header"            : "header.jpg",
	#"Icon"                : "N\A.jpg",         # https://stackoverflow.com/a/24693219/8175291
	"1. Cover (1x)"        : "library_600x900.jpg",
	#"Cover (2x)"          : "library_600x900_2x.jpg", # not used
	"2. Page BG"           : "library_hero.jpg",
	"3. Page BG (Blured)"  : "library_hero_blur.jpg",
	"4. Logo (transparent)": "logo.png",
}

print("Hi")
#presdb_repo = {}
#presdb_local = {}
presence_data_persistent = {}
settings = {}


#
def is_exist_file(_file_path):
	#print("Checking is exist \"" + str(_presdb_path) +"\" file... ", end='')
	if os.path.isfile(_file_path):
		#print("done. yes.")
		return True
	#print("done. no.")
	return False

def is_exist_file_crit(_file_path):
	if not is_exist_file(_file_path):
		raise SystemExit("No \"" + _file_path + "\" file. Aborting run.")

def _save_general_file(_file_path, _file_data):
	#print("Saving \"" + str(_presdb_path) +"\" file... ", end='')
	with open(_file_path, "w", encoding='utf-8') as _general_file:
		_general_file.write(_file_data)
		_general_file.close()
	#print("done.")

def _read_general_file(_file_path):
	#print("Reading \"data/presence_db_repo.json\" file... ", end='')
	with open(_file_path, "r", encoding='utf-8') as _general_file:
		_data = _general_file.read()
		_general_file.close()
		return _data
	#print("done.")

def _save_json_file(_file_path, _file_data):
	#print("Saving \"" + str(_presdb_path) +"\" file... ", end='')
	_save_general_file(_file_path, json.dumps(_file_data, indent=2) + "\n")
	#print("done.")

def _read_json_file(_file_path):
	#print("Reading \"data/presence_db_repo.json\" file... ", end='')
	with open(_file_path, "r", encoding='utf-8') as _general_file:
		_data = json.load(_general_file)
		_general_file.close()
		return _data
	#print("done.")


#
def _save_presdb(_presdb_path, _presdb_data):
	_save_json_file(_presdb_path, _presdb_data)

def _read_presdb(_presdb_path):
	return _read_json_file(_presdb_path)

#
def save_presdb_repo(_presdb_data):
	#print("save_presdb_repo() called")
	_save_presdb("data/presence_db_repo.json", _presdb_data)

def save_presdb_local(_presdb_data):
	#print("save_presdb_local() called")
	_save_presdb("data/presence_db_local.json", _presdb_data)

#
def read_presdb_repo():
	#print("read_presdb_repo() called")
	global presdb_repo
	presdb_repo = _read_presdb("data/presence_db_repo.json")

def read_presdb_local():
	#print("read_presdb_local() called")
	global presdb_local
	presdb_local = _read_presdb("data/presence_db_local.json")

#
def checkexist_presdb_repo():
	#print("checkexist_presdb_repo() called")
	global presdb_repo
	_path = "data/presence_db_repo.json"
	if is_exist_file(_path):
		read_presdb_repo()
	else:
		print("No \"" + str(_path) +"\" file, creating...")
		save_presdb_repo({})

def checkexist_presdb_local():
	#print("checkexist_presdb_local() called")
	global presdb_local
	_path = "data/presence_db_local.json"
	if is_exist_file(_path):
		read_presdb_local()
	else:
		print("No \"" + str(_path) +"\" file, creating...")
		save_presdb_local({})

def checkexist_presdbs():
	#print("checkexist_presdbs() called")
	global presdb_repo
	global presdb_local
	checkexist_presdb_repo()
	checkexist_presdb_local()

#
def checkexist_settings(_settings_path = "data/settings.json"):
	#print("checkexist_settings() called")
	global settings
	if not os.path.isfile(_settings_path):
		raise SystemExit("No \"" + str(_settings_path) + "\" file")
	else:
		with open(_settings_path, "r", encoding='utf-8') as settings_data_f:
			settings = json.load(settings_data_f)
			#settings_data_f.close()

#
def misc_checks():
	#print("misc_checks() called")
	global settings
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


#
def read_steam_conf():
	global loginusers
	with open(settings["path_steam_core"] + "/config/loginusers.vdf", "r", encoding='utf-8') as vdf_text:
		loginusers = vdf.parse(vdf_text)
		#input_data_f.close()

	if not "users" in loginusers:
		raise SystemExit("no \"loginusers\" param in \"<Steam>/config/loginusers.vdf\" file")

	if len(loginusers["users"].keys()) != 1:
		raise SystemExit("Wrong \"users\" length, check file \"<Steam>/config/loginusers.vdf\"")

	# Todo: See "Steam/config/config.vdf"
	#print("loginusers:", vdf.dumps(loginusers, pretty=True))
	user_SteamID = SteamID(list(loginusers["users"].keys())[0])
	print("SteamID:", user_SteamID.as_64, "AccountID:", user_SteamID.account_id)

	tmp_path = settings["path_steam_core"] + "/userdata/" + str(user_SteamID.account_id) + "/config/localconfig.vdf"
	print("tmp_path:", tmp_path)
	with open(tmp_path, "r", encoding='utf-8') as vdf_text:
		localconfig = vdf.parse(vdf_text)
		#input_data_f.close()

	#print("localconfig:", localconfig)
	avatar_hash = localconfig["UserLocalConfigStore"]["friends"][str(user_SteamID.account_id)]["avatar"]
	apps = list(localconfig["UserLocalConfigStore"]["Software"]["valve"]["Steam"]["apps"].keys())
	apps_config = list(localconfig["UserLocalConfigStore"]["UserAppConfig"].keys())
	depots = list(localconfig["UserLocalConfigStore"]["depots"].keys())
	print("localconfig: (avatar):", avatar_hash, "(apps):", len(apps), "(apps_config):", len(apps_config), "(depots):", len(depots))
	print("https://avatars.akamai.steamstatic.com/" + avatar_hash + "_full.jpg")
	# "Steam\config\avatarcache"


checkexist_presdbs()

checkexist_settings()
misc_checks()
#read_steam_conf()


### USE THIS: http://gaming.stackexchange.com/a/364904/292725 ###
### USE THIS: http://gaming.stackexchange.com/a/364904/292725 ###
### USE THIS: http://gaming.stackexchange.com/a/364904/292725 ###
is_exist_file_crit("data/input.json")

input_data = _read_json_file("data/input.json")
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
max_data_threshold = len(base_urls.keys())
min_data_threshold = 0
errors_count = 0
errors_threshold = max_data_threshold * 2
print('justify len:', just_len, "max_data_threshold:", max_data_threshold)


# https://stackoverflow.com/a/1112350/8175291
def signal_handler(sig, frame):
	print()
	#print("presence_data_persistent:", presence_data_persistent)
	print('You pressed Ctrl-C!')
	#sys.exit(0)
	save_presdb_repo(presence_data_persistent)
	exit()

signal.signal(signal.SIGINT, signal_handler)
#print('Press Ctrl+C')
#signal.pause()

for appid_int in input_data:
	appid_str = str(appid_int)

	global presdb_repo
	global presdb_local

	presence_data_persistent = presence_data_persistent
	presence_data_temp = {}
	presence_locally = None
	presence_locally_count = 0
	missing_remote_db = None
	missing_remote = None
	missing_count = 0

	for surl_name, surl in base_urls.items():
		url_index = surl #str(list(base_urls.values()).index(surl)) #surl_name

		tmp_url = base_url + appid_str + "/" + surl
		tmp_name = appid_str + "_" + surl
		tmp_file = settings["path_output"] + "\\" + tmp_name

		presence_locally = os.path.isfile(tmp_file)
		tmp_status1 = appid_str.ljust(longest_gameid + 1) + surl.split('.')[0].ljust(longest_base_url - 3)  #'"' + tmp_name + '":'

		print(tmp_status1.ljust(just_len), end='')


		# Preventing app from Steam ««DOS»» bombing
		missing_remote_db = False
		if presence_data_persistent.get(appid_str) != None:
			if type(presence_data_persistent[appid_str]) is dict:
				if presence_data_persistent[appid_str][url_index] == 404:
					missing_remote_db = True

		if missing_remote_db:
			tmp_status2 = "ERR"
			tmp_status3 = "404 Not Found (DB)"
			print(tmp_status2.ljust(3), tmp_status3)
			presence_data_temp.update({url_index: True})
			continue

		if presence_locally:
			presence_locally_count = presence_locally_count
			presence_locally_count += 1
			tmp_status2 = "OK"
			tmp_status3 = "409 Already found (locally)" #exists locally
			print(tmp_status2.ljust(3), tmp_status3)
			presence_data_temp.update({url_index: 409})
			continue


		#tmp_status2 = "↓… " #"DOWNLOAD… " #"💾" #"Downloading... "
		#print("File not exist, start downloading...")
		#print(tmp_status2, end='')

		try:
			with urllib.request.urlopen(tmp_url) as f_web:
				f_out = f_web.read() #.decode('utf-8')
				with open(tmp_file, "wb") as fcont:
					fcont.write(f_out)
				tmp_status2 = "OK" #"Downloaded successfully"
				tmp_status3 = "200 OK"  #exists locally  #str(e.code) + " " + str(e.reason)
				print(tmp_status2.ljust(3), tmp_status3)
				presence_data_temp.update({url_index: True})

		except HTTPError as e:
			# "e" can be treated as a http.client.HTTPResponse object
			tmp_status2 = "ERR"
			missing_count += 1

			if e.code == 404:
				tmp_status3 = str(e.code) + " " + str(e.reason) # remotely # on Steam
				presence_data_temp.update({url_index: e.code})

			elif e.code == 429:
				tmp_status3 = str(e.code) + " " + str(e.reason)
				print(tmp_status2.ljust(3), tmp_status3)
				print(str(datetime.now()) + " Stoped bombing Steam.")
				presence_data_temp.update({url_index: e.code})
				#errors_count += 1

				presence_data_persistent.update(presence_data_temp)
				save_presdb_repo(presence_data_persistent)
				exit()

			else:
				errors_count += 1
				tmp_status3 = "HTTPError:" + str(e.code)

			print(tmp_status2.ljust(3), tmp_status3)

		except URLError as e:
			# https://stackoverflow.com/a/29538780/8175291
			tmp_status2 = "ERR"
			tmp_status3 = "URLError:" + str(e.reason)
			print(tmp_status2.ljust(3), tmp_status3)
			presence_data_temp.update({url_index: str(e)})
			missing_count += 1
			errors_count += 1
		#else:
		#	tmp_status2 = "Downloaded successfully"
		#	print("File \"" + tmp_name + "\" -", tmp_status2)

	#if missing_count == min_data_threshold:
	#	presence_data_temp = True
	#if missing_count == max_data_threshold:
	#	presence_data_temp = False
	#if presence_locally_count == max_data_threshold:
	#	presence_data_temp = 409

	if presence_data_persistent.get(appid_str) != None:
		presence_data_temp = {appid_str: presence_data_temp}
		presence_data_persistent.update(presence_data_temp)
	else:
		presence_data_persistent[appid_str] = presence_data_temp

	save_presdb_repo(presence_data_persistent)

	if errors_count > errors_threshold:
		raise SystemExit("Too many errors, aborting.")
		exit()


print("Bye")
exit()

