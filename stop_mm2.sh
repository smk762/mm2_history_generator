#!/bin/bash
./megabot.py cancel_orders
source userpass
curl --url "http://127.0.0.1:7784" --data "{\"userpass\":\"$userpass\",\"method\":\"stop\"}"
echo
