# mm2_history_generator

This tool is intended to generate a long swap history for multiple coins to assist with stess testing our GUI apps.
Note: EVM coins/tokens with high fees (ERC20/BEP20) and some newer protocols are excluded.

**It has only been tested on linux, and likely needs some modifications to run on other OS.**
**The MEGABOT will set a low or negative margin for automated trades - do not run this with a seed that has funds you dont want to lose!**

### Prerequistes:
- Clone this repo with submodules `git clone https://github.com/smk762/mm2_history_generator -recurse-submodules`
- Install pip packages `pip3 install -r requirements.txt`
- Download or build https://github.com/KomodoPlatform/atomicDEX-API and place `mm2` binary in the root folder of this repository


### To Use:
- create a `.env` file, and add an entry called `SEED` for your seedphrase.
- Run `./megabot.py configure` to create the `MM2.json` and `userpass` files
- Launch mm2 with `./start_mm2.sh`
- Run `./megabot.py activate` to activate coins (e.g. to check balances) without creating orders (do before starting bot!)
- Run `./megabot.py start_bot` to place orders at 1% under market for all pair combinations of coins with balance in your wallet.
- Run `./megabot.py balances` to view balances of coins with a balance.
- Run `./megabot.py zhtlc_status` to activation status of ZHTLC coins.
- Run `./megabot.py orders` to view currently placed orders (wait 5 min after starting bot so that these are populated)
- Run `./megabot.py scalp` to buy from any orders in orderbook for pairs you have funds for in your wallet, where the sell price is under cex price. This will run in a loop, so exit with `Ctl-C`
- Stop the makerbot with `./megabot.py stop_bot`
- Stop mm2 with `./stop_mm2.sh`
- Cancel all existing orders with `./cancel_orders`

- Update to the latest coins in master branch of https://github.com/KomodoPlatform/coins with `./update_coins.sh`

If trading ZHTLC coins, you will need to wait for the coins cache to download first. You can still start the bot, and once the ZHTLC coin(s) are fully activated, you can stop the bot with `./megabot.py stop_bot` and then restart the bot with `./megabot.py start_bot` again. Wait at least 5 mins between stopping and restarting the bot so the final loop cycle will expire and you can start it again. Once a ZHTLC coin is fully activated, you will see its balance when running `./megabot.py balances`

Leave this running overnight on a wallet with a small amount of many currencies which do not have high fee costs, and over time a long swap history will be generated.

Ideally, run this alongside someone else so there are lots of undermarket trades on the orderbook.

**Be careful not to add large funds to any wallet using this seed, as you will be selling at under CEX price.**

**Bonus features:**
- Because `./megabot.py activate` batch enables almost every coin (> 500), it can be a useful tool to identify which coins you might have forgotten balances on.
- The MM2.json created by `./megabot.py configure` will use a different port (7784) so can be run alongside other mm2 instances. It has also defines the `DB` folder to be same as one used by Desktop, so you should be able to view history in GUI.

