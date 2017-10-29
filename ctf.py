#/usr/bin/env python3

import os
import sys
import subprocess
import argparse
import configparser
from pathlib import Path
from ruamel.yaml import YAML
from collections import ChainMap

default = [".", "scripts", "skel", ".git"]

def updateYAML(chall_info):
	chall_list = []
	yaml       = YAML()
	dcconf     = yaml.load("version: '3'\n\nservices:")

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

def parseYAML(config_list):
	yaml = YAML()
    
	def load_file(p):
		y = yaml.load(p)
		for section in y:
			y[section]['Path'] = p.parent
		return y

	configs = ChainMap(*[load_file(i) for i in config_list])

	for c in configs.values():
		result = c.get('Name'), c.get('Port'), c.get('Type'), c.get('Path')
		if all(result):
			yield result

def getYAMLList():
	defaults = set(default)
	f = Path.cwd().glob("**/config.yml")
	return (p for p in f if not defaults & set(p.parts))

def update():
	config_list = getYAMLList()
	chall_info = parseYAML(config_list)
	updateYAML(chall_info)

def remove():
	config_list = getYAMLList()
	chall_info = parseYAML(config_list)

	for root, dirs, files in os.walk('.'):
		dirs[:] = [d for d in dirs if d not in default]
		break

	subprocess.run(["docker-compose", "stop"])

	for item in zip(chall_info, dirs):
		chall, c_dir = item
		name, port, c_type, cdir = chall
		subprocess.run(["./scripts/delete.sh", name])

	subprocess.run(["./scripts/remove.sh"])

def fly():
	build()
	update()
	subprocess.run(["docker-compose", "up", "-d"])

def build():
	config_list = getYAMLList()
	chall_info = parseYAML(config_list)

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
	parser.add_argument("-f", "--fly",
						help="deploy new challenges on the fly",
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
	if args.fly:
		fly()
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
