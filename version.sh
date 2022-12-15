#!/bin/bash
source userpass
curl --url "http://127.0.0.1:7784" --data "{\"method\":\"version\",\"userpass\":\"$userpass\"}"
echo ""
