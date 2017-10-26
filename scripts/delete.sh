#!/bin/bash
if [ $# -eq 0 ]; then
	echo "./delete.sh <name>"
	exit
fi

NAME=$1
NAME_LOWER=$(echo "${NAME}" | tr '[:upper:]' '[:lower:]')
CONTAINER_ID=$(docker ps -aq --filter name="${NAME_LOWER}")

if [[ "${CONTAINER_ID}" ]]; then
	echo "Removing container id "${CONTAINER_ID}" with name ${NAME_LOWER}"
	docker rm "${CONTAINER_ID}" --force
fi

docker rmi --force "${NAME_LOWER}"
