#!/bin/bash

function usage(){
	echo -e "Usage: ./gen.sh -n foo -p 9999 [OPTION]"
	echo -e "Generate CTF challenge docker images."
	echo -e "  -n NAME\tName of your challenge"
	echo -e "  -p PORT\tPort the challenge is served on"
	echo -e "  -d DIR\tPath to a directory containing your challenge"
	echo -e "  -w\t\tBuild a docker image with flask"
	echo -e "  -f\t\tSpecify that a flag file exists"
	echo -e "  -m\t\tSpecify that a makefile exists"
	echo -e "  -v\t\tVerbose output (set -x)"
	echo -e "  -h\t\tHelp screen"
	exit
}

while getopts n:p:d:fwmvh option; do
	case "${option}" in
		n) NAME=${OPTARG};;
		p) PORT=${OPTARG};;
		d) DIR=${OPTARG};;
		f) FLAG=true;;
		w) WEB=true;;
		m) MAKE=true;;
		v) VERB=true;;
		h) HELP=true;;
		*) exit;;
	esac
done

if [[ "${HELP}" ]]; then
	usage
fi

if [[ "${VERB}" ]]; then
	set -x
fi

if [[ -z "${NAME}" ]]; then
	echo "You must provide at least a challenge name [-n]."
	exit
elif [[ -z "${PORT}" ]]; then
	echo "You must provide a port to serve the challenge on [-p]."
	exit
elif [[ ${PORT} != ?(-)+([0-9]) || ${PORT} -gt 65535 ]]; then
	echo "Port { "${PORT}" } is not a valid port."
	exit
fi

NAME_LOWER=$(echo "${NAME}" | tr '[:upper:]' '[:lower:]')
cp -R build-skel/ "${NAME}-build" && mkdir "${NAME}-build"/bin

if [[ "${DIR}" ]]; then
	if [[ -d "${DIR}" ]]; then
		echo -e "[\e[92mPASS\e[39m] Challenge: Directory \"${DIR}\" found."
		cp -r "${DIR}"/* "${NAME}-build"/bin
	else
		echo -e "[\e[91mERROR\e[39m] Challenge: Directory \"${DIR}\" not found."
		exit
	fi
fi

cd "${NAME}-build"

if [[ "${WEB}" ]]; then
	mv Dockerfile-web Dockerfile
	sed -i 's/__ctf__/'"${NAME_LOWER}"'/g' build
	if [[ ! -f bin/app.py ]]; then
		echo -e "[\e[91mFAIL\e[39m] Flask: File \"bin/app.py\" not found."
	else
		echo -e "[\e[92mPASS\e[39m] Flask: File \"bin/app.py\" found."
		sed -i 's/__port__/'"${PORT}"'/g' bin/app.py
	fi
	rm __ctf__.xinetd start.sh Dockerfile-bin
	exit
else
	mv Dockerfile-bin Dockerfile
	rm Dockerfile-web
fi

mv __ctf__.xinetd "${NAME}".xinetd

if [[ "${MAKE}" ]]; then
	sed -i '/make/s/^#//g' Dockerfile
fi

if [[ "${FLAG}" ]]; then
	sed -i '/flag/s/^#//g' Dockerfile
fi

sed -i 's/__ctf__/'"${NAME}"'/g' "${NAME}".xinetd Dockerfile
sed -i 's/__ctf__/'"${NAME_LOWER}"'/g' build
sed -i 's/__port__/'"${PORT}"'/g' "${NAME}".xinetd Dockerfile build
