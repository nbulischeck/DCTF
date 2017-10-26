#!/bin/bash
find ../ -name "*-build" -type d | xargs rm -rf
docker network prune -f
