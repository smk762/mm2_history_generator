#!/usr/bin/env python3
import os
import sys
import json
import time
import string
import random
import os.path
import mnemonic
import requests
from dotenv import load_dotenv
import lib_mm2

load_dotenv()
SEED = os.getenv('SEED')
MARGIN = os.getenv('MARGIN')
if MARGIN:
    MARGIN = float(MARGIN)
TRADE_ONLY = os.getenv('TRADE_ONLY')
if TRADE_ONLY:
    TRADE_ONLY = TRADE_ONLY.split(" ")
PORT = 7784

script_path = os.path.abspath(os.path.dirname(__file__))
os.chdir(script_path)

from os.path import expanduser
HOME = expanduser("~")
dbdir = f"{HOME}/.atomic_qt"
if not os.path.exists(f"{dbdir}"):
    os.makedirs(f"{dbdir}")

def colorize(string, color):
    colors = {
        'red':'\033[31m',
        'yellow':'\033[33m',
        'magenta':'\033[35m',
        'blue':'\033[34m',
        'green':'\033[32m'
    }
    if color not in colors:
        return str(string)
    else:
        return colors[color] + str(string) + '\033[0m'

error_coins = {}
activation_commands = requests.get("http://116.203.120.91:8762/api/atomicdex/coin_activation_commands/").json()
coins = list(activation_commands.keys())
coins.sort()
for coin in coins:
    #print(activation_commands[coin])
    resp = lib_mm2.mm2_proxy(activation_commands[coin])
    if "error" in resp:
        print(f"Error with {coin}: {resp['error']}")
        error_coins.update({coin: resp["error"]})
    else:
        print(colorize(f"{coin} address: {resp['address']}, balance: {resp['balance']}", "green"))


print(error_coins)

