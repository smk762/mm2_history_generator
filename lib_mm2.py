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

def get_userpass():
    with open('userpass', 'r') as f:
        contents = f.read()
        return contents.replace("userpass=", "")

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

from os.path import expanduser
HOME = expanduser("~")
dbdir = f"{HOME}/.atomic_qt"
if not os.path.exists(f"{dbdir}"):
    os.makedirs(f"{dbdir}")

def mm2_proxy(params):
    if "userpass" in params:
        params["userpass"] = get_userpass()
        params["mm2"] = 1
    r = requests.post(f"http://127.0.0.1:{PORT}", json.dumps(params))
    resp = r.json()
    if "error" in resp:
        if not resp["error"].find("already initialized") > -1:
            print(colorize(resp, 'red'))
        if resp["error"].find("Userpass is invalid") > -1:
            print(colorize("MM2 is rejecting your rpc_password. Please check you are not running mm2 or AtomicDEX-Desktop app, and your rpc_password conforms to constraints in https://developers.komodoplatform.com/basic-docs/atomicdex/atomicdex-setup/configure-mm2-json.html#mm2-json", "red"))
            sys.exit()
    return resp

def get_orderbook(base, rel):
    params = {
        "mmrpc": "2.0",
        "userpass": get_userpass(),
        "method": "orderbook",
        "params": {
            "base": base,
            "rel": rel
        },
        "id": 0
    }
    return mm2_proxy(params)

def stop_bot():
    params = {
    "userpass": get_userpass(),
    "mmrpc": "2.0",
    "method": "stop_simple_market_maker_bot",
    "params": {},
    "id": 0
    }
    print(mm2_proxy(params))


def cancel_orders():
    params = {
    "userpass": get_userpass(),
    "method": "cancel_all_orders",
    "cancel_by": {
            "type": "All"
        }
    }
    print(mm2_proxy(params))


def start_bot(coins, exclude=None):
    print(f"MARGIN: {MARGIN}")
    cfg = {}
    print(coins)
    print(f"Coins with a balance: {coins}")
    if TRADE_ONLY:
        coins = TRADE_ONLY
    if exclude:
        coins = [i for i in coins if i not in exclude]
    print(f"Starting bot with {coins}")
    for base in coins:
        for rel in coins:
            if (base != rel and rel not in ["KMD", "BTC"]):
                if not MARGIN:
                    if base == "KMD": spread = "1.01"
                    else: spread = "0.99"
                else:
                    spread = 1 + MARGIN/100
                cfg.update({
                    f"{base}/{rel}": {
                        "base": base,
                        "rel": rel,
                        "min_volume": {"percentage": "0.25"},
                        "max_volume": {"percentage": "0.50"},
                        "spread": spread,
                        "base_confs": 3,
                        "base_nota": False,
                        "rel_confs": 3,
                        "rel_nota": False,
                        "enable": True,
                        "price_elapsed_validity": 300.0,
                        "check_last_bidirectional_trade_thresh_hold": True
                    }
                })
    params = {
        "userpass": get_userpass(),
        "mmrpc": "2.0",
        "method": "start_simple_market_maker_bot",
        "params": {
            "price_url": "https://prices.komodo.live/api/v2/tickers?expire_at=600",
            "bot_refresh_rate": 300,
            "cfg": cfg
        }
    }
    print(mm2_proxy(params))

def get_orders():
    params = {
        "userpass": get_userpass(),
        "method": "my_orders"
    }
    resp = mm2_proxy(params)
    print("\nMaker Orders")
    for i in resp["result"]["maker_orders"]:
        order = resp["result"]["maker_orders"][i]
        print(f"{order['base']}/{order['rel']}: {order['available_amount']} {order['base']} available. {len(order['started_swaps'])} swaps started")
    print("\nTaker Orders")
    for i in resp["result"]["taker_orders"]:
        print(f"{order['base']}/{order['rel']}: {i}")
    print(f'{len(resp["result"]["maker_orders"])} Maker orders and {len(resp["result"]["taker_orders"])} Taker orders active')

def buy(base, rel, sell_price, volume):
    params = {
        "userpass": get_userpass(),
        "method": "buy",
        "base": base,
        "rel": rel,
        "price": sell_price,
        "volume": volume
    }
    return mm2_proxy(params)


def scalp(coins):
    prices = requests.get("https://prices.komodo.live/api/v2/tickers?expire_at=600").json()
    for base in coins:
        for rel in coins:
            prices_base = base.split("-")[0]
            prices_rel = rel.split("-")[0]
            if (base != rel and len({prices_base, prices_rel} & set(prices.keys())) == 2):
                try:
                    base_cex_price = prices[prices_base]["last_price"]
                    rel_cex_price = prices[prices_rel]["last_price"]
                    cex_price = float(base_cex_price)/float(rel_cex_price)
                    print(f"\n{base}/{rel} cex_price: {cex_price}")
                    print(f"Getting {base}/{rel} orderbook")
                    resp = get_orderbook(base, rel)
                    asks = resp["result"]["asks"]
                    for i in asks:
                        if not i["is_mine"]:
                            sell_coin = i["coin"] # base, the coin on offer
                            sell_price = float(i["price"]["decimal"]) # 'x' base per rel
                            maxvol = i["base_min_volume"]["decimal"]  # base volume on offer
                            minvol = i["base_min_volume"]["decimal"]  # min volume per trade offer
                            print(f"{base}/{rel} sell_price: {sell_price}")
                            if sell_price < cex_price:
                                volume = (float(maxvol) + float(minvol)) / 2
                                print(colorize(f"Buying {volume} {base} for {sell_price * volume} {rel}", 'green'))
                                resp = buy(base, rel, sell_price, volume)
                                time.sleep(3)
                except Exception as e:
                    print(e)
                    pass

def get_enabled_coins():
    coins = []
    payload = {
        "userpass": get_userpass(),
        "method": "get_enabled_coins"
    }
    resp = mm2_proxy(payload)
    for i in resp["result"]:
        coins.append(i['ticker'])
    return coins

def get_balances():
    enabled_coins = get_enabled_coins()
    coins_with_balance = []
    batch = []
    for coin in enabled_coins:
        batch.append({
            "userpass": get_userpass(),
            "method": "my_balance",
            "coin": coin
        })
    resp = mm2_proxy(batch)
    print("\n=== BALANCES ===")
    for i in resp:
        if 'balance' in i:
            if float(i["balance"]) > 0:
                print(i)
                coins_with_balance.append(i["coin"])
    print("\n")
    return coins_with_balance

def get_zhtlc_status_v2():
    payload = []
    for i in range(10):
        params = {
            "userpass": get_userpass(),
            "method": "task::enable_z_coin::status",
            "mmrpc": "2.0",
            "params": {
                "task_id": i
            }
        }
        payload.append(params)
    resp = mm2_proxy(payload)
    for i in resp:
        print(i)

def get_zhtlc_status():
    payload = []
    for i in range(10):
        params = {
            "userpass": get_userpass(),
            "method": "init_z_coin_status",
            "mmrpc": "2.0",
            "params": {
                "task_id": i
            }
        }
        payload.append(params)
    resp = mm2_proxy(payload)
    for i in resp:
        print(i)


def get_erc_activation(userpass, protocol_file, coin_info):
    data = get_rpc_nodes_data(protocol_file)
    payload = {
        "userpass": get_userpass(),
        "method": "enable",
        "coin": coin_info["coin"],
        "urls": [i["url"] for i in data["rpc_nodes"]],
        "swap_contract_address": data["swap_contract_address"]
    }
    if "fallback_swap_contract" in data:
        payload.update({"fallback_swap_contract": data["fallback_swap_contract"]})
    return payload

def get_utxo_activation(userpass, coin_info):
    payload = {
        "userpass": get_userpass(),
        "method": "electrum",
        "coin": coin_info["coin"],
        "servers": get_electrums(coin_info["coin"]),
        "tx_history": True
    }
    return payload

def get_zhtlc_activation(userpass, coin_info):
    payload = {
        "method": "init_z_coin",
        "mmrpc": "2.0",
        "userpass": get_userpass(),
        "params": {
            "ticker": coin_info["coin"],
            "activation_params": {
                "mode": {
                    "rpc": "Light",
                    "rpc_data": {
                        "electrum_servers": get_electrums(coin_info["coin"]),
                        "light_wallet_d_servers": get_light_wallet_d_servers(coin_info["coin"])
                    }
                }
            }
        }
    }
    return payload

def get_zhtlc_activation_v2(userpass, coin_info):
    payload = {
        "method": "task::enable_z_coin::init",
        "mmrpc": "2.0",
        "userpass": get_userpass(),
        "params": {
            "ticker": coin_info["coin"],
            "activation_params": {
                "mode": {
                    "rpc": "Light",
                    "rpc_data": {
                        "electrum_servers": get_electrums(coin_info["coin"]),
                        "light_wallet_d_servers": get_light_wallet_d_servers(coin_info["coin"])
                    }
                }
            }
        }
    }
    return payload