#!/usr/bin/python3.8
# 
# Author: jon4hz
# Date: 09.03.2020
# Desc: testing stream as class
#
#####################################################################################################################################################

import configparser
from unicorn_binance_websocket_api.unicorn_binance_websocket_api_manager import BinanceWebSocketApiManager
import logging
import time
import threading
import os


logging.basicConfig(level=logging.INFO,
                    filename=os.path.basename(__file__) + '.log',
                    format="{asctime} [{levelname:8}] {process} {thread} {module}: {message}",
                    style="{")


config = configparser.ConfigParser()
config.read('config.ini')

api_key = config['binance-futures']['api_key']
api_secret = config['binance-futures']['api_secret']

class socket:
    def __init__(self, exchange, stream, coin):
        self.coin = coin
        self.exchange = exchange
        self.stream = stream
        self.binance_futures_websocket = BinanceWebSocketApiManager(exchange=self.exchange)

    def print_stream_data_from_stream_buffer(self, binance_websocket_api_manager):
        while True:
            if binance_websocket_api_manager.is_manager_stopping():
                exit(0)
            self.oldest_stream_data_from_stream_buffer = binance_websocket_api_manager.pop_stream_data_from_stream_buffer()
            if self.oldest_stream_data_from_stream_buffer is False:
                time.sleep(0.01)
            else:
                print(self.oldest_stream_data_from_stream_buffer)

    def start(self):
        user_data_stream = self.binance_futures_websocket.create_stream(self.stream, self.coin, api_key=api_key, api_secret=api_secret, output='dict')
        worker_thread = threading.Thread(target=self.print_stream_data_from_stream_buffer, args=(self.binance_futures_websocket,))
        worker_thread.start()
        return user_data_stream
    def stop(self, stream):
        self.binance_futures_websocket.stop_stream(stream)

#socket = socket('binance.com-futures', '!userData')
print(1)
socket1 = socket('binance.com', 'miniTicker', 'BTCUSDT')
x = socket1.start()
socket2 = socket('binance.com', 'miniTicker', 'ETHUSDT')
print(2)
socket2.start()
time.sleep(4)
socket1.stop(x)
print('Stop stuff')