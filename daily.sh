#!/bin/bash

cd "$(dirname "$0")"

/opt/anaconda3/bin/python src/download.py

docker_id=$(docker ps | grep "learn_english" | cut -f1 -d" ")
docker container stop $docker_id

./run.sh
