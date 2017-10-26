#!/bin/bash
if [ $# -eq 0 ]; then
	echo "./delete.sh <name>"
	exit
fi

NAME=$1
NAME_LOWER=$(echo "${NAME}" | tr '[:upper:]' '[:lower:]')
CONTAINER_ID=$(docker ps -a | grep "${NAME}" | awk '{print $1}')
IMAGE_ID=$(docker images | grep "${NAME_LOWER}" | awk '{print $1}')

if [[ ${CONTAINER_ID} ]]; then
	docker rm "${CONTAINER_ID}"
fi

if [[ ${IMAGE_ID} ]]; then
	docker rmi --force "${NAME_LOWER}"
fi
