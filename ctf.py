#/usr/bin/env python

import os
import sys
import json
import subprocess
import argparse
import configparser
from pprint import pprint
from pathlib import Path, PurePath
from ruamel.yaml import YAML
from collections import ChainMap

default = [".", "scripts", "skel", "images", ".git"]

def fbctf_categories():
	config_list = getYAMLList()
	chall_info = parseYAML(config_list, "config")
	categories = {
		"categories":[
			{"category": "None", "protected": True},
			{"category": "Quiz", "protected": True}
		]
	}
	cat_list = []
	for c in chall_info:
		cat = c.get("category")
		if cat not in cat_list:
			cat_list.append(cat)
	for i in cat_list:
		cat = {"category": i, "protected": False}
		categories["categories"].append(cat)

	with open("./configs/fbctf_categories.json", "w+") as config:
		config.write(json.dumps(categories, indent=4))

def fbctf_levels():
	config_list = getYAMLList()
	chall_info = parseYAML(config_list, "config")
	levels = {"levels": []}

	with open("./configs/assets/iso.txt") as f:
		iso = [line.rstrip() for line in f]

	for c, i in zip(chall_info, iso):
		defaults = {
			"type": "flag",
			"active": False,
			"entity_iso_code": i,
			"attachments": [],
			"links": [],
			"bonus": 0,
			"bonus_dec": 0,
			"bonus_fix": 0,
			"penalty": 0
		}
		c['description'] += "\nPort: " + str(c['port'])
		c.pop("port")
		c.update(defaults)
		levels["levels"].append(c)

	with open("./configs/fbctf_levels.json", "w+") as config:
		config.write(json.dumps(levels, indent=4))

def platform(p):
	if p.lower() == "fbctf":
		fbctf_categories()
		fbctf_levels()
	else:
		print(p.lower(), "platform not found.")

def updateYAML(chall_info):
	chall_list = []
	yaml       = YAML()
	dcconf     = {"version": '3', "services": None}

	for chall in chall_info:
		name, port, c_type, cdir = chall
		challenge = dict()
		ports = ["{port}:{port}".format(port=port)]
		challenge[name] = {'image': name.lower(), 'ports': ports}
		if dcconf['services'] is None:
			dcconf['services'] = challenge
		else:
			dcconf['services'].update(challenge)

	with open("docker-compose.yml", "w+") as config:
		yaml.dump(dcconf, config)

def parseYAML(config_list, reason):
	yaml = YAML()

	def load_file(p):
		y = yaml.load(p)
		for section in y:
			y[section]['path'] = p.parent
		return y

	configs = ChainMap(*[load_file(i) for i in config_list])

	if reason == "docker":
		for c in configs.values():
			if c.get('serve') == True:
				result = c.get('title'), c.get('port'), c.get('category'), c.get('path')
				if all(result):
					yield result

	elif reason == "config":
		for c in configs.values():
			for i in ["path", "serve"]:
				c.pop(i)
			yield c

def getYAMLList():
	defaults = set(default)
	f = Path.cwd().glob("**/config.yml")
	return (p for p in f if not defaults & set(p.parts))

def update():
	config_list = getYAMLList()
	chall_info = parseYAML(config_list, "docker")
	updateYAML(chall_info)

def remove():
	config_list = getYAMLList()
	chall_info = parseYAML(config_list, "docker")

	for root, dirs, files in os.walk('.'):
		dirs[:] = [d for d in dirs if d not in default]
		break

	subprocess.run(["docker-compose", "stop"])

	for challenge, challenge_dir in zip(chall_info, dirs):
		name, port, c_type = chall
		subprocess.run(["./scripts/delete.sh", name])

	subprocess.run(["./scripts/remove.sh"])

def build():
	config_list = getYAMLList()
	chall_info = parseYAML(config_list, "docker")

	for chall in chall_info:
		name, port, ctype, cdir = chall
		if ctype == "web":
			subprocess.run(["./scripts/gen.sh", "-n", name,
								"-p", str(port), "-d", cdir, "-w"])	
		else:
			subprocess.run(["./scripts/gen.sh", "-n", name,
								"-p", str(port), "-d", cdir, "-f"])
		buildpath = ''.join(["./", name, "-build/build"])
		subprocess.run([buildpath])

def parse_args():
	parser = argparse.ArgumentParser(description="Docker-based CTF Platform")
	state = parser.add_mutually_exclusive_group()
	parser.add_argument("-b", "--build",
						help="build the docker images",
						action="store_true")
	state.add_argument("-u", "--up",
						help="start the CTF",
						action="store_true")
	state.add_argument("-d", "--down",
						help="stop the CTF",
						action="store_true")
	parser.add_argument("-s", "--status",
						help="displays the status of the challenges",
						action="store_true")
	parser.add_argument("-r", "--remove",
						help="remove all ctf containers and images",
						action="store_true")
	parser.add_argument("--platform",
						help="generate frontend config",
						choices=["fbctf", "ctfd"])
	parser.add_argument("--update",
						help="update the docker compose config",
						action="store_true")

	if len(sys.argv[1:]) == 0:
		parser.print_help()

	return parser.parse_args()

def main():
	args = parse_args()

	if args.update:
		update()
	if args.build:
		build()
	if args.up:
		update()
		subprocess.run(["docker-compose", "up", "-d"])
	elif args.down:
		subprocess.run(["docker-compose", "down"])
	if args.fly:
		fly()
	if args.status:
		subprocess.run(["docker-compose", "ps"])
	if args.platform:
		platform(args.platform)
	if args.remove:
		remove()

if __name__ == "__main__":
	main()
