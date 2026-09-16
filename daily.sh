#!/bin/bash

cd "$(dirname "$0")"

uv run src/download.py

docker_id=$(docker ps | grep "learn_english" | cut -f1 -d" ")
docker container restart $docker_id

