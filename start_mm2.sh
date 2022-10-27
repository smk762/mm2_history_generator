#!/bin/bash
source userpass
export MM_COINS_PATH="$(pwd)/coins/coins"
stdbuf -oL ./mm2 > mm2.log &
sleep 3
curl --url "http://127.0.0.1:7783" --data "{\"method\":\"version\",\"userpass\":\"$userpass\"}"
tail -f mm2.log
