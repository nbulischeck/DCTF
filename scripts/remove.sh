#!/bin/bash
find ../ -name "*-build" -type d | xargs rm -rf && rm -rf ../docker-compose.yml
docker network prune -f
