#/usr/bin/env python3

import os
import sys
import subprocess
import argparse
import configparser
from ruamel.yaml import YAML
from pathlib import Path

default = [".", "scripts", "skel", ".git"]

def updateYAML(chall_info):
	chall_list = []
	yaml       = YAML()
	dcconf     = yaml.load("version: '3'\n\nservices:")

	for chall in chall_info:
		name, port, c_type = chall
		challenge = dict()
		ports = ["{port}:{port}".format(port=port)]
		challenge[name] = {'image': name.lower(), 'ports': ports}
		if dcconf['services'] is None:
			dcconf['services'] = challenge
		else:
			dcconf['services'].update(challenge)

	with open("docker-compose.yml", "w+") as config:
		yaml.dump(dcconf, config)

def parseINI(config_list):
	chall_info = []
	name, port, c_type = None, None, None
	config = configparser.ConfigParser()
	config.read(config_list)

	for section in config.sections():
		name = config.get(section, "name")
		port = config.get(section, "port")
		c_type = config.get(section, "type")
		if name and port and c_type:
			chall_info.append([name, port, c_type])
		name, port, c_type = None, None, None

	return chall_info

def getINIList():
	defaults = set(default)
	f = Path.cwd().glob("**/config.ini")
	return (p for p in f if not defaults & set(p.parts))

def update():
	config_list = getINIList()
	chall_info = parseINI(config_list)
	updateYAML(chall_info)

def remove():
	config_list = getINIList()
	chall_info = parseINI(config_list)

	for root, dirs, files in os.walk('.'):
		dirs[:] = [d for d in dirs if d not in default]
		break

	subprocess.run(["docker-compose", "stop"])

	for item in zip(chall_info, dirs):
		chall, c_dir = item
		name, port, c_type = chall
		subprocess.run(["./scripts/delete.sh", name])

	subprocess.run(["./scripts/remove.sh"])

def build():
	config_list = getINIList()
	chall_info = parseINI(config_list)

	for root, dirs, files in os.walk('.'):
		dirs[:] = [d for d in dirs if d not in default]
		break

	for item in zip(chall_info, dirs):
		chall, c_dir = item
		name, port, c_type = chall
		if c_type == "binary":
			subprocess.run(["./scripts/gen.sh", "-n", name,
							"-p", port, "-d", c_dir, "-f"])
		elif c_type == "web":
			subprocess.run(["./scripts/gen.sh", "-n", name,
							"-p", port, "-d", c_dir, "-w"])
		buildpath = ''.join(["./", name, "-build/build"])
		subprocess.run([buildpath])

def main():
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
	parser.add_argument("-p", "--prune",
						help="prune unused docker networks",
						action="store_true")
	parser.add_argument("--update",
						help="update the docker compose config",
						action="store_true")
	args = parser.parse_args()

	if args.update:
		update()
	if args.build:
		build()
	if args.up:
		update()
		subprocess.run(["docker-compose", "up", "-d"])
	elif args.down:
		subprocess.run(["docker-compose", "down"])
	if args.status:
		subprocess.run(["docker-compose", "ps"])
	if args.prune:
		subprocess.run(["docker", "network", "prune"])
	if args.remove:
		remove()

	if len(sys.argv[1:]) == 0:
		parser.print_help()

if __name__ == "__main__":
	main()
