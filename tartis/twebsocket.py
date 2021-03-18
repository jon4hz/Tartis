from unicorn_binance_websocket_api import BinanceWebSocketApiManager
import time, threading, logging, os

logging.basicConfig(level=logging.INFO,
                    filename=os.path.basename(__file__) + '.log',
                    format="{asctime} [{levelname:8}] {process} {thread} {module}: {message}",
                    style="{")

class websocket:
    def __init__(self, exchange, stream, coin, api_key=None, api_secret=None):
        self.coin = coin
        self.exchange = exchange
        self.stream = stream
        self.binance_websocket = BinanceWebSocketApiManager(exchange=self.exchange)
        self.api_key = api_key
        self.api_secret = api_secret

    def write_data_to_database(self, binance_websocket_api_manager):
        while True:
            if binance_websocket_api_manager.is_manager_stopping():
                exit(0)
            self.oldest_stream_data_from_stream_buffer = binance_websocket_api_manager.pop_stream_data_from_stream_buffer()
            if self.oldest_stream_data_from_stream_buffer is False:
                time.sleep(0.01)
            else:
                print(self.oldest_stream_data_from_stream_buffer)

    def start(self):
        user_data_stream = self.binance_websocket.create_stream(self.stream, self.coin, api_key=self.api_key, api_secret=self.api_secret, output='dict')
        worker_thread = threading.Thread(target=self.write_data_to_database, args=(self.binance_websocket,))
        worker_thread.start()
        return user_data_stream
    def stop(self, stream):
        self.binance_websocket.stop_stream(stream)