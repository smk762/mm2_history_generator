# mm2_history_generator

This tool is intended to generate a long swap history for multiple coins to assist with testing our GUI apps.
Note: EVM coins/tokens with high fees (ERC20/BEP20) and some newer protocols are excluded.

**It has only been tested on linux, and likely needs some modifications to run on other OS.**
**By default, the MEGABOT will set a low or negative margin for automated trades - do not run this with a seed that has funds you dont want to lose!**

### Prerequistes:
- Clone this repo with submodules `git clone https://github.com/smk762/mm2_history_generator -recurse-submodules`
- Install pip packages `pip3 install -r requirements.txt`
- Download or build https://github.com/KomodoPlatform/atomicDEX-API and place `mm2` binary in the root folder of this repository


### To Use:
- Create a `.env` file, and add an entry called `SEED` for your seedphrase.
- Optionally, you can also add to the `.env` a numeric value with an entry called `MARGIN` to set a more profitable spread on orders (a value of 1 = 1% over CEX market price).
- Optionally, you can also add to the `.env` a list of tickers with an entry called `TRADE_ONLY` to select a smaller set of coins to be included in bot order placements).
- Run `./megabot.py configure` to create the `MM2.json` and `userpass` files
- Launch mm2 with `./start_mm2.sh`
- Run `./megabot.py activate` to activate coins (and check balances) without creating orders (**do before starting bot!**)
- Run `./megabot.py start_bot` to place automated bot orders for all pair combinations of coins with balance in your wallet.
- Run `./megabot.py start_bot_without_zhtlc` to place orders for all pair combinations of coins with balance in your wallet except ZHTLC coins.
- Run `./megabot.py balances` to view balances of coins with a balance.
- Run `./megabot.py zhtlc_status` to activation status of ZHTLC coins.
- Run `./megabot.py orders` to view currently placed orders (wait 5 min after starting bot so that these are populated)
- Run `./megabot.py cancel_orders` to cancel all active orders.
- Run `./megabot.py scalp` to buy from any orders in orderbook for pairs you have funds for in your wallet, where the sell price is under cex price.
- Run `./megabot.py scalp_loop` to buy from any orders in orderbook for pairs you have funds for in your wallet, where the sell price is under cex price. This will run in a loop, so exit with `Ctl-C`
- Stop the makerbot with `./megabot.py stop_bot`
- Stop mm2 with `./stop_mm2.sh` (this will also cancel any currently placed orders before exiting).
- Cancel all existing orders with `./cancel_orders`

- Update to the latest coins in master branch of https://github.com/KomodoPlatform/coins with `./update_coins.sh`

If trading ZHTLC coins, you will need to wait for the coins cache to download first. You can still start the bot, and once the ZHTLC coin(s) are fully activated, you can stop the bot with `./megabot.py stop_bot` and then restart the bot with `./megabot.py start_bot` again. Wait at least 5 mins between stopping and restarting the bot so the final loop cycle will expire and you can start it again. Once a ZHTLC coin is fully activated, you will see its balance when running `./megabot.py balances`

Leave this running overnight on a wallet with a small amount of many currencies which do not have high fee costs, and over time a long swap history will be generated.

Ideally, run this alongside someone else so there are lots of undermarket trades on the orderbook.

**Be careful not to add large funds to any wallet using this seed, as you will be selling at under CEX price.**

**Bonus features:**
- Because `./megabot.py activate` batch enables almost every coin (> 500), it can be a useful tool to identify which coins you might have forgotten balances on.
- The MM2.json created by `./megabot.py configure` will use a different port (7784) and rename `mm2` to `mm2_megabot` so can be run alongside other mm2 instances. It has also defines the `DB` folder to be same as one used by Desktop, so you should be able to view history in GUI.


### To change mm2 versions

As we change the binary filename so it doesnt get killed when launching the desktop app, the following steps are recommended when changing mm2 version for testing.
- Run `./stop_mm2.sh` or `pkill -9 mm2_megabot` to stop the current session
- Delete binary: `rm mm2_megabot` 
- Download and unzip (or copy over) the `mm2` binary version you want to test.
- Run `./start_mm2.sh` - This will rename the binary if it has not already been renamed before launching.


### .env file example
```
SEED="your seed phrase words go here"
MARGIN=3                              # i.e. 3% margin over CEX price
TRADE_ONLY="KMD LTC DGB"              # Optional, only create bot orders for pairs including these coins (otherwise all coins will balance will be included)
```


**Note: To cover both ZHTLC method sets, both will be called, and you will see errors for the one that is not present in the mm2 version you are using. You can ignore these errors.**

For example:

```
Error: {'mmrpc': '2.0', 'error': 'No such method', 'error_path': 'dispatcher', 'error_trace': 'dispatcher:188]', 'error_type': 'NoSuchMethod', 'id': None}
Task ID [0] for ZHTLC returned
Error: {'mmrpc': '2.0', 'error': 'No such method', 'error_path': 'dispatcher', 'error_trace': 'dispatcher:188]', 'error_type': 'NoSuchMethod', 'id': None}
Task ID [1] for ZHTLC returned
```

Checking status also will return errors from whichever method set is not available, and some for non-existent or finished task IDs (by default it checks task_id values in range 0-9). 

{'mmrpc': '2.0', 'error': 'No such method', 'error_path': 'dispatcher', 'error_trace': 'dispatcher:188]', 'error_type': 'NoSuchMethod', 'id': None}
{'mmrpc': '2.0', 'error': 'No such method', 'error_path': 'dispatcher', 'error_trace': 'dispatcher:188]', 'error_type': 'NoSuchMethod', 'id': None}
{'mmrpc': '2.0', 'error': 'No such method', 'error_path': 'dispatcher', 'error_trace': 'dispatcher:188]', 'error_type': 'NoSuchMethod', 'id': None}
{'mmrpc': '2.0', 'error': 'No such method', 'error_path': 'dispatcher', 'error_trace': 'dispatcher:188]', 'error_type': 'NoSuchMethod', 'id': None}
{'mmrpc': '2.0', 'error': 'No such method', 'error_path': 'dispatcher', 'error_trace': 'dispatcher:188]', 'error_type': 'NoSuchMethod', 'id': None}
{'mmrpc': '2.0', 'error': 'No such method', 'error_path': 'dispatcher', 'error_trace': 'dispatcher:188]', 'error_type': 'NoSuchMethod', 'id': None}
{'mmrpc': '2.0', 'error': 'No such method', 'error_path': 'dispatcher', 'error_trace': 'dispatcher:188]', 'error_type': 'NoSuchMethod', 'id': None}
{'mmrpc': '2.0', 'error': 'No such method', 'error_path': 'dispatcher', 'error_trace': 'dispatcher:188]', 'error_type': 'NoSuchMethod', 'id': None}
{'mmrpc': '2.0', 'error': 'No such method', 'error_path': 'dispatcher', 'error_trace': 'dispatcher:188]', 'error_type': 'NoSuchMethod', 'id': None}
{'mmrpc': '2.0', 'error': 'No such method', 'error_path': 'dispatcher', 'error_trace': 'dispatcher:188]', 'error_type': 'NoSuchMethod', 'id': None}
{'mmrpc': '2.0', 'result': {'status': 'InProgress', 'details': {'BuildingWalletDb': {'current_scanned_block': 2167027, 'latest_block': 2196911}}}, 'id': None}
{'mmrpc': '2.0', 'error': "No such task '1'", 'error_path': 'init_standalone_coin', 'error_trace': 'init_standalone_coin:133]', 'error_type': 'NoSuchTask', 'error_data': 1, 'id': None}
{'mmrpc': '2.0', 'error': "No such task '2'", 'error_path': 'init_standalone_coin', 'error_trace': 'init_standalone_coin:133]', 'error_type': 'NoSuchTask', 'error_data': 2, 'id': None}
{'mmrpc': '2.0', 'error': "No such task '3'", 'error_path': 'init_standalone_coin', 'error_trace': 'init_standalone_coin:133]', 'error_type': 'NoSuchTask', 'error_data': 3, 'id': None}
{'mmrpc': '2.0', 'error': "No such task '4'", 'error_path': 'init_standalone_coin', 'error_trace': 'init_standalone_coin:133]', 'error_type': 'NoSuchTask', 'error_data': 4, 'id': None}
{'mmrpc': '2.0', 'error': "No such task '5'", 'error_path': 'init_standalone_coin', 'error_trace': 'init_standalone_coin:133]', 'error_type': 'NoSuchTask', 'error_data': 5, 'id': None}
{'mmrpc': '2.0', 'error': "No such task '6'", 'error_path': 'init_standalone_coin', 'error_trace': 'init_standalone_coin:133]', 'error_type': 'NoSuchTask', 'error_data': 6, 'id': None}
{'mmrpc': '2.0', 'error': "No such task '7'", 'error_path': 'init_standalone_coin', 'error_trace': 'init_standalone_coin:133]', 'error_type': 'NoSuchTask', 'error_data': 7, 'id': None}
{'mmrpc': '2.0', 'error': "No such task '8'", 'error_path': 'init_standalone_coin', 'error_trace': 'init_standalone_coin:133]', 'error_type': 'NoSuchTask', 'error_data': 8, 'id': None}
{'mmrpc': '2.0', 'error': "No such task '9'", 'error_path': 'init_standalone_coin', 'error_trace': 'init_standalone_coin:133]', 'error_type': 'NoSuchTask', 'error_data': 9, 'id': None}
