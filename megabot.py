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
ethereum_coins = [f for f in os.listdir(f"{coins_path}/ethereum") if os.path.isfile(f"{coins_path}/ethereum/{f}")]
print(f"{coins_path}/utils/coins_config.json")
with open(f"{coins_path}/utils/coins_config.json", "r") as f:
    coins_json = json.load(f)
with open(f"{coins_path}/slp/bchd_urls.json", "r") as f: bchd_urls = json.load(f)
with open(f"{coins_path}/coins", "r") as f: coins_file = json.load(f)

protocols = {
    "AVAX": "AVX-20",
    "BNB": "BEP-20",
    "ETC": "Ethereum Classic",
    "ETH": "ERC-20",
    "ETH-ARB20": "Arbitrum",
    "FTM": "FTM-20",
    "GLMR": "Moonbeam",
    "HT": "HecoChain",
    "KCS": "KRC-20",
    "MATIC": "Matic",
    "MOVR": "Moonriver",
    "ONE": "HRC-20",
    "QTUM": "QRC-20",
    "RBTC": "RSK Smart Bitcoin",
    "SBCH": "SmartBCH",
    "SLP": "SLPTOKEN",
    "UBQ": "Ubiq"
}

testnet_protocols = {
    "AVAXT": "AVX-20",
    "BNBT": "BEP-20",
    "FTMT": "FTM-20",
    "tSLP": "SLPTOKEN",
    "tQTUM": "QRC-20",
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

def get_userpass():
    with open('userpass', 'r') as f:
        contents = f.read()
        return contents.replace("userpass=", "")

def create_mm2_json():
    conf = {
        "gui": "History_Spammer_Tool",
        "netid": 7777,
        "rpcport": PORT,
        "rpc_password": "",
        "passphrase": SEED,
        "userhome": HOME,
        "dbdir": f"{HOME}/.atomic_qt"
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

def get_erc_activation(userpass, protocol_file, coin_info):
    data = get_rpc_nodes_data(protocol_file)
    payload = {
        "userpass": userpass,
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
        "userpass": userpass,
        "method": "electrum",
        "coin": coin_info["coin"],
        "servers": get_electrums(coin_info["coin"]),
        "tx_history": True
    }
    return payload

def batch_activate():
    userpass = get_userpass()
    utxo_enable = []
    erc_enable = []
    for coin in coins_json:
        coin_info = coins_json[coin]
        coin_type = coin_info["type"]
        if coin in lightwallet_coins:
            # ZHTLC activation
            pass
        elif coin in electrum_coins:
            utxo_enable.append(get_utxo_activation(userpass, coin_info))
            pass
        elif coin_type != "SLP":
            if coin_info["is_testnet"]:
                if testnet_protocols_reversed[coin_type] in ethereum_coins:
                    erc_enable.append(get_erc_activation(userpass, testnet_protocols_reversed[coin_type], coin_info))
                else:
                    print(f"Coin activation not covered yet for {coin}")
            elif coin_type in protocols_reversed:
                if protocols_reversed[coin_type] in ethereum_coins:
                    erc_enable.append(get_erc_activation(userpass, protocols_reversed[coin_type], coin_info))
                else:
                    print(f"Coin activation not covered yet for {coin}")
            else:
                print(f"Coin activation not covered yet for {coin}")
        else:
            print(f"Coin activation not covered yet for {coin}")
    params = utxo_enable + erc_enable
    resp = mm2_proxy(params)
    errors = 0
    no_balance = 0
    coins_with_balance = []
    for i in resp:
        if "error" in i:
            errors += 1
            # print(f"Error: {i}")
        else:
            if float(i['balance']) > 0:
                print(f"{i['address']} | {i['coin']} | {i['balance']} ")
                coins_with_balance.append(i['coin'])
            else:
                no_balance += 1
    print(f"{len(coins_with_balance)} coins with balance activated")
    print(f"{no_balance} coins without balance also activated")
    print(f"{errors} coins with error when trying to activate")
    return coins_with_balance

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

def start_bot(coins):
    cfg = {}
    for base in coins:
        for rel in coins:
            if (base != rel
                and len({base, rel} & set(protocols.keys())) == 0
                and len({base, rel} & set(testnet_protocols.keys())) == 0
                and rel != "KMD"):
                if base == "KMD": spread = "1.01"
                else: spread = "0.99"
                cfg.update({
                    f"{base}/{rel}": {
                        "base": base,
                        "rel": rel,
                        "max": True,
                        "min_volume": {"percentage": "0.25"},
                        "spread": spread,
                        "base_confs": 3,
                        "base_nota": False,
                        "rel_confs": 3,
                        "rel_nota": False,
                        "enable": True,
                        "price_elapsed_validity": 90.0,
                        "check_last_bidirectional_trade_thresh_hold": True
                    }
                })
    params = {
        "userpass": get_userpass(),
        "mmrpc": "2.0",
        "method": "start_simple_market_maker_bot",
        "params": {
            "price_url": "https://prices.komodo.live:1313/api/v2/tickers?expire_at=600",
            "bot_refresh_rate": 120,
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
    prices = requests.get("https://prices.komodo.live:1313/api/v2/tickers?expire_at=600").json()
    for base in coins:
        for rel in coins:
            prices_base = base.split("-")[0]
            prices_rel = rel.split("-")[0]
            if (base != rel
                and rel not in protocols.keys()
                and len({base, rel} & set(testnet_protocols.keys())) == 0
                and len({prices_base, prices_rel} & set(prices.keys())) == 2
                and rel != "KMD"):
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

def get_balances():
    coins_with_balance = []
    batch = []
    for coin in coins_json.keys():
        batch.append({
            "userpass": get_userpass(),
            "method": "my_balance",
            "coin": coin
        })
    resp = mm2_proxy(batch)
    for i in resp:
        if 'balance' in i:
            if float(i["balance"]) > 0:
                print(i)
                coins_with_balance.append(i["coin"])
    return coins_with_balance

def mm2_proxy(params):
    r = requests.post(f"http://127.0.0.1:{PORT}", json.dumps(params))
    resp = r.json()
    if "error" in resp:
        print(colorize(resp, 'red'))
        if resp["error"].find("Userpass is invalid") > -1:
            print(colorize("MM2 is rejecting your rpc_password. Please check you are not running mm2 or AtomicDEX-Desktop app, and your rpc_password conforms to constraints in https://developers.komodoplatform.com/basic-docs/atomicdex/atomicdex-setup/configure-mm2-json.html#mm2-json", "red"))
            sys.exit()
    return resp

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'start_bot':
            coins_with_balance = batch_activate()
            start_bot(coins_with_balance)
        elif sys.argv[1] == 'configure':
            create_mm2_json()
        elif sys.argv[1] == 'activate':
            batch_activate()
        elif sys.argv[1] == 'orders':
            get_orders()
        elif sys.argv[1] == 'scalp':
            while True:
                coins_with_balance = get_balances()
                time.sleep(90)
                scalp(coins_with_balance)
                print("\n======================================================\n")
                time.sleep(90)
        else:
            print("Invalid option! Choose from ['start_bot', 'activate', 'configure', 'orders', 'scalp']")
    else:
        print("No action! Choose from ['start_bot', 'activate', 'configure', 'orders', 'scalp']")