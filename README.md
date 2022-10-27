# mm2_history_generator

This tool is intended to generate a long swap history for multiple coins to assist with stess testing our GUI apps.

Prerequistes:
- Clone this repo with submodules `git clone https://github.com/smk762/mm2_history_generator -recurse-submodules`
- Install pip packages `pip3 install -r requirements.txt`
- Download or build https://github.com/KomodoPlatform/atomicDEX-API and place `mm2` binary in the root folder of this repository

To Use:
- create a `.env` file, and add an entry called `SEED` for your seedphrase.
- Run `./megabot.py configure` to create the `MM2.json` and `userpass` files
- Launch mm2 with `./start_mm2.sh`
- (optional) Run `./megabot.py activate` to activate coins (e.g. to check baances) without creating orders
- Run `./megabot.py start_bot` to place orders at 1% under market for all pair combinations of coins with balance in your wallet.
- Run `./megabot.py orders` to view currently placed orders
- Run `./megabot.py scalp` to buy from any orders in orderbook for pairs you have funds for in your wallet, where the sell price is under cex price.
- Stop mm2 with `stop_mm2.sh`

Leave this running overnight on a wallet with a small amount of many currencies which do not have high fee costs, and over time a long swap history will be generated.

Ideally, run this alongside someone else so there are lots of undermarket trades on the orderbook.
Be careful not to add large funds to any wallet, as you will be selling at under CEX price.

**Bonus feature:** Because `./megabot.py activate` batch enables almost every coin (> 500), it can be a useful tool to identify which coins you might have forgotten balances on.
