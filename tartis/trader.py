import ccxt
from . import error

class trader:
    def __init__(self, exchange, api_key, api_secret, uid=None, api_password=None):
        self.exchange = exchange
        self.api_key = api_key
        self.api_secret = api_secret
        self.uid = uid
        self.api_password = api_password


        if self.exchange.lower() == 'binance':
            self.exchange = ccxt.binance(
                {
                    'enableRateLimit': True,
                    'apiKey': self.api_key,
                    'secret': self.api_secret
                }
            )

        elif self.exchange.lower() == 'binance_futures':
            self.exchange = ccxt.binance(
                { 
                    'option': { 'defaultMarket': 'future' },
                    'enableRateLimit': True,
                    'apiKey': self.api_key,
                    'secret': self.api_secret
                }
            )
        else:
            raise error.WrongExchange

    def check_api(self):
        self.exchange.checkRequiredCredentials()

    def get_account_balance(self):
        if self.exchange.has.get('fetchBalance'):
            return self.exchange.fetch_balance()

    def get_open_orders(self, symbol):
        if self.exchange.has.get('fetchOpenOrders'):
            return self.exchange.fetch_open_orders(symbol)