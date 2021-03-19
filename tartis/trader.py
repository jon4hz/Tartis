import ccxt
import threading, time, os, sqlite3
from unicorn_binance_websocket_api import BinanceWebSocketApiManager
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

class market_data():
    def __init__(self, exchange, stream, coin, database):
        self.coin = coin
        self.stream = stream
        self.exchange = exchange
        self.binance_websocket = BinanceWebSocketApiManager(exchange=self.exchange)
        self.database = database

    def handle_market_data_stream(self, binance_websocket_api_manager):
        while True:
            if binance_websocket_api_manager.is_manager_stopping():
                exit(0)
            self.oldest_stream_data_from_stream_buffer = binance_websocket_api_manager.pop_stream_data_from_stream_buffer()
            if self.oldest_stream_data_from_stream_buffer is False:
                time.sleep(0.01)
            else:
                # check trading database
                self.con = sqlite3.connect(self.database)
                self.cur = self.con.cursor()
                self.con.close()
                
                

    def start(self):
        self.user_data_stream = self.binance_websocket.create_stream(self.stream, self.coin, output='dict')
        self.worker_thread = threading.Thread(target=self.handle_market_data_stream, args=(self.binance_websocket,))
        self.worker_thread.start()
        return self.user_data_stream

    def stop(self, stream):
        self.binance_websocket.stop_stream(stream)