#!/usr/bin/python3.8
# 
# Author: jon4hz
# Date: 26.12.2020
# Desc: testing userdata stream
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

def print_stream_data_from_stream_buffer(binance_websocket_api_manager):
    while True:
        if binance_websocket_api_manager.is_manager_stopping():
            exit(0)
        oldest_stream_data_from_stream_buffer = binance_websocket_api_manager.pop_stream_data_from_stream_buffer()
        if oldest_stream_data_from_stream_buffer is False:
            time.sleep(0.01)
        else:
            print(oldest_stream_data_from_stream_buffer)

binance_futures_websocket = BinanceWebSocketApiManager(exchange="binance.com-futures")

user_data_stream = binance_futures_websocket.create_stream('arr', '!userData', api_key=api_key, api_secret=api_secret, output='dict')

worker_thread = threading.Thread(target=print_stream_data_from_stream_buffer, args=(binance_futures_websocket,))
worker_thread.start()