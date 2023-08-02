#!/bin/bash
source userpass
export MM_COINS_PATH="$(pwd)/coins/coins"
cp mm2 mm2_megabot 		# rename binary and use non default port so using desktop will not kill this session.
stdbuf -oL ./mm2_megabot > mm2_megabot.log &
sleep 3
curl --url "http://127.0.0.1:7784" --data "{\"method\":\"version\",\"userpass\":\"$userpass\"}"
echo
echo "check API logs with tail -f mm2_megabot.log"
