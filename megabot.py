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
from lib_mm2 import *

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

coins_path = f"{script_path}/coins"
lightwallet_coins = [f for f in os.listdir(f"{coins_path}/light_wallet_d") if os.path.isfile(f"{coins_path}/light_wallet_d/{f}")]
electrum_coins = [f for f in os.listdir(f"{coins_path}/electrums") if os.path.isfile(f"{coins_path}/electrums/{f}")]
evm_parent_coins = [f for f in os.listdir(f"{coins_path}/ethereum") if os.path.isfile(f"{coins_path}/ethereum/{f}")]
with open(f"{coins_path}/utils/coins_config.json", "r") as f:
    coins_json = json.load(f)
with open(f"{coins_path}/slp/bchd_urls.json", "r") as f: bchd_urls = json.load(f)
with open(f"{coins_path}/coins", "r") as f: coins_file = json.load(f)


# Excluding ERC20 and BEP20 so fees dont drain funds too fast

protocols = {
    "AVAX": "AVX-20",
    "ETH": "ERC-20",
    "BNB": "BEP-20",
    "ETC": "Ethereum Classic",
    "ETH-ARB20": "Arbitrum",
    "FTM": "FTM-20",
    "GLMR": "Moonbeam",
    "HT": "HecoChain",
    "KCS": "KRC-20",
    "MATIC": "Matic",
    "MOVR": "Moonriver",
    "ONE": "HRC-20",
    "RBTC": "RSK Smart Bitcoin",
    "SBCH": "SmartBCH",
    "UBQ": "Ubiq"
}

testnet_protocols = {
    "AVAXT": "AVX-20",
    "BNBT": "BEP-20",
    "FTMT": "FTM-20",
    "tSLP": "SLPTOKEN",
    "MATICTEST": "Matic",
    "UBQ": "Ubiq"
}

protocols_reversed = {}
for k, v in protocols.items():
    protocols_reversed.update({v: k})

testnet_protocols_reversed = {}
for k, v in testnet_protocols.items():
    testnet_protocols_reversed.update({v: k})

def generate_rpc_pass(length):
    special_chars = ["@", "-", "_", '^']
    rpc_pass = ""
    quart = int(length/4)
    while len(rpc_pass) < length:
        rpc_pass += ''.join(random.sample(string.ascii_lowercase, random.randint(1,quart)))
        rpc_pass += ''.join(random.sample(string.ascii_uppercase, random.randint(1,quart)))
        rpc_pass += ''.join(random.sample(string.digits, random.randint(1,quart)))
        rpc_pass += ''.join(random.sample(special_chars, random.randint(1,quart)))
    str_list = list(rpc_pass)
    random.shuffle(str_list)
    return ''.join(str_list)

def create_userpass_file(userpass):
    with open('userpass', 'w') as f:
        f.write(f"userpass={userpass}")
        print("userpass created")


def create_mm2_json():
    conf = {
        "gui": "History_Spammer_Tool",
        "netid": 7777,
        "rpcport": PORT,
        "rpc_password": "",
        "passphrase": SEED,
        "userhome": HOME,
        "dbdir": f"{HOME}/.atomic_qt/mm2/DB"
    }
    userpass = generate_rpc_pass(16)
    create_userpass_file(userpass)
    conf.update({"rpc_password": userpass})
    with open("MM2.json", "w+") as f:
        json.dump(conf, f, indent=4)
    print("MM2.json created")

def get_rpc_nodes_data(protocol_file):
    with open(f"{coins_path}/ethereum/{protocol_file}", "r") as f:
        return json.load(f)

def get_electrums(coin):
    with open(f"{coins_path}/electrums/{coin}", "r") as f:
        return json.load(f)

def get_light_wallet_d_servers(coin):
    with open(f"{coins_path}/light_wallet_d/{coin}", "r") as f:
        return json.load(f)


def batch_activate(exclude=None):
    if not exclude:
        exclude = []
    userpass = get_userpass()
    utxo_enable = []
    erc_enable = []
    zhtlc_enable = []
    for coin in coins_json:
        if coin not in exclude:
            coin_info = coins_json[coin]
            coin_type = coin_info["type"]
            if coin in lightwallet_coins:
                zhtlc_enable.append(get_zhtlc_activation(userpass, coin_info))
                zhtlc_enable.append(get_zhtlc_activation_v2(userpass, coin_info))
            elif coin in electrum_coins:
                utxo_enable.append(get_utxo_activation(userpass, coin_info))
            elif coin_type != "SLP":
                if coin_info["is_testnet"]:
                    if coin_type in testnet_protocols_reversed:
                        if testnet_protocols_reversed[coin_type] in evm_parent_coins:
                            erc_enable.append(get_erc_activation(userpass, testnet_protocols_reversed[coin_type], coin_info))
                        else:
                            print(f"Coin activation not covered yet for {coin} (testnet A)")
                    else:
                        print(f"Coin activation not covered yet for {coin} (testnet B)")
                elif coin_type in protocols_reversed:
                    if protocols_reversed[coin_type] in evm_parent_coins:
                        erc_enable.append(get_erc_activation(userpass, protocols_reversed[coin_type], coin_info))
                    else:
                        print(f"Coin activation not covered yet for {coin} (not erc)")
                else:
                    print(f"Coin activation not covered yet for {coin} (not in protocols)")
            else:
                print(f"Coin activation not covered yet for {coin} (SLP)")
    params = utxo_enable + erc_enable + zhtlc_enable
    print("Waiting for batch RPC response...")
    resp = mm2_proxy(params)
    active = 0
    errors = 0
    no_balance = 0
    coins_with_balance = []
    for i in resp:
        if "error" in i:
            if i["error"].find("already initialized") > -1:
                active += 1
                msg = i["error"].split("]")[-1]
                print(msg)
            else:
                errors += 1
                print(f"Error: {i}")
        else:
            if 'result' in i:
                if 'task_id' in i['result']:
                    print(f"Task ID [{i['result']['task_id']}] for ZHTLC returned")
                elif float(i['balance']) > 0:
                    print(f"{i['address']} | {i['coin']} | {i['balance']} ")
                    coins_with_balance.append(i['coin'])
                else:
                    no_balance += 1
    print(f"{active} coins already activated")
    print(f"{len(coins_with_balance)} coins with balance activated")
    print(f"{coins_with_balance}")
    print(f"{no_balance} coins without balance also activated")
    print(f"{errors} coins with error when trying to activate")
    return coins_with_balance


if __name__ == '__main__':
    available_methods = ['start_bot', 'start_bot_without_zhtlc', 'stop_bot', 'configure', 'activate', 'balances', 'orders', 'cancel_orders', 'scalp', 'scalp_loop', 'zhtlc_status']
    if len(sys.argv) > 1:
        if sys.argv[1] == 'start_bot':
            coins_with_balance = get_balances()
            start_bot(coins_with_balance)
        elif sys.argv[1] == 'start_bot_without_zhtlc':
            coins_with_balance = get_balances()
            start_bot(coins_with_balance, ["ARRR", "ZOMBIE"])
        elif sys.argv[1] == 'stop_bot':
            stop_bot()
        elif sys.argv[1] == 'configure':
            create_mm2_json()
        elif sys.argv[1] == 'activate':
            batch_activate()
        elif sys.argv[1] == 'activate_without_zhtlc':
            batch_activate(["ARRR", "ZOMBIE"])
        elif sys.argv[1] == 'orders':
            get_orders()
        elif sys.argv[1] == 'cancel_orders':
            cancel_orders()
        elif sys.argv[1] == 'balances':
            get_balances()
        elif sys.argv[1] == 'zhtlc_status':
            get_zhtlc_status()
            get_zhtlc_status_v2()
        elif sys.argv[1] == 'scalp':
            while True:
                scalp(coins_with_balance)
        elif sys.argv[1] == 'scalp_loop':
            coins_with_balance = get_balances()
            while True:
                time.sleep(60)
                scalp(coins_with_balance)
                coins_with_balance = get_balances()
        else:
            print(f"Invalid option! Choose from {available_methods}")
    else:
        print(f"No action! Choose from {available_methods}")
