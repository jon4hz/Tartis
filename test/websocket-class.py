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
import asyncio


logging.basicConfig(level=logging.INFO,
                    filename=os.path.basename(__file__) + '.log',
                    format="{asctime} [{levelname:8}] {process} {thread} {module}: {message}",
                    style="{")


config = configparser.ConfigParser()
config.read('config.ini')

api_key = config['binance-futures']['api_key']
api_secret = config['binance-futures']['api_secret']

class socket:
    def __init__(self, exchange, stream, market):
        self.market = market
        self.exchange = exchange
        self.stream = stream
        self.bsm = BinanceWebSocketApiManager(exchange=self.exchange, process_stream_data=self.callback)


    async def process_data(self, stream_data, stream_buffer_name=False):
        # filter of events
        print(stream_data)
    

    def callback(self, stream_data, stream_buffer_name=False):
        asyncio.ensure_future(self.process_data(stream_data, stream_buffer_name))
            

    def start_websocket(self, bsm, stream, market):
        self.user_data_stream = self.bsm.create_stream(self.stream, self.market, api_key=api_key, api_secret=api_secret, output='dict')
        print(threading.get_ident())

    def start(self):
        self.worker_thread = threading.Thread(target=self.start_websocket, args=(self.bsm, self.stream, self.market))
        self.worker_thread.start()

    def stop(self):
        self.bsm.stop_stream(self.user_data_stream)


print(threading.get_ident())
loop = asyncio.new_event_loop()
#socket = socket('binance.com-futures', '!userData')
socket1 = socket('binance.com', 'miniTicker', 'BTCUSDT')
socket1.start()
socket2 = socket('binance.com', 'miniTicker', 'ETHUSDT')
socket2.start()
time.sleep(4)
socket1.stop()
print('socket1 stopped')