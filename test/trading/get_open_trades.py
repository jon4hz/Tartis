import os, sys, ccxt

# pylint: disable=no-name-in-module
from ccxt.base.errors import (
    AuthenticationError
)
# pylint: enable=no-name-in-module

# sys hacking for tartis import (parent folder)
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
second_parentdir = os.path.dirname(parentdir)
sys.path.append(parentdir)
sys.path.append(second_parentdir)

# pylint: disable=import-error
import tartis
# pylint: enable=import-error
from config import *

trader = tartis.trader.trader('binance', api_key, api_secret)

try:
    trader.check_api()
except AuthenticationError as e:
    print(f"Error authentication error: {e}")

print(trader.get_open_orders('BTC/USDT'))