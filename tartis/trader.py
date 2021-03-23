import ccxt
import threading, time, os, psycopg2, decimal
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
    def __init__(self, exchange, stream, coin):
        self.coin = coin
        self.stream = stream
        self.exchange = exchange

        if self.exchange == 'binance.com' or self.exchange == 'binance.com-futures':
            self.binance_websocket = BinanceWebSocketApiManager(exchange=self.exchange)

    def handle_market_data_stream(self, binance_websocket_api_manager, pool, symbol, bot):
        
        f_digits = 0
        
        while True:
            if binance_websocket_api_manager.is_manager_stopping():
                exit(0)
            oldest_stream_data_from_stream_buffer = binance_websocket_api_manager.pop_stream_data_from_stream_buffer()
            if oldest_stream_data_from_stream_buffer is False:
                time.sleep(0.01)
            else:
                msg = oldest_stream_data_from_stream_buffer.get('data')
                if msg:
                    # check trading database
                    conn = pool.getconn()
                    cur = conn.cursor()

                    cur.execute(
                    f'''
                        SELECT trades.id, symbol, direction, exchange, entries.price, entries.percent, entries.filled, tps.price, tps.percent, tps.filled, sls.price, sls.percent, sls.filled, telegram_message_id, telegram_channel_id FROM trades

                        LEFT OUTER JOIN entries ON trades.id=entries.trade_id
                        LEFT OUTER JOIN tps ON trades.id=tps.trade_id
                        LEFT OUTER JOIN sls ON trades.id=sls.trade_id

                        WHERE   close_time IS NULL AND
                                channel_trade = TRUE AND
                                symbol = '{symbol}'
                    '''
                    )
                    data = cur.fetchall()
                    trades = {}
                    for i in data:
                        try:
                            offset = 0
                            for j in ['entries', 'tps', 'sls']:
                                if sum(trades[i[0]][j]['percent']) != 100:
                                    trades[i[0]][j]['point'].append(i[4+offset])
                                    trades[i[0]][j]['percent'].append(i[5+offset])
                                    trades[i[0]][j]['filled'].append(i[6+offset])
                                offset += 3

                        except KeyError:
                            trades[i[0]] = {
                                'symbol': i[1],
                                'direction': i[2],
                                'exchange': i[3],
                                'telegram_message_id': i[13],
                                'telegram_channel_id': i[14],
                                'entries': {
                                    'point': [],
                                    'percent': [],
                                    'filled': []
                                },
                                'tps': {
                                    'point': [],
                                    'percent': [],
                                    'filled': []
                                },
                                'sls': {
                                    'point': [],
                                    'percent': [],
                                    'filled': []
                                },
                            }
                            offset = 0
                            for j in ['entries', 'tps', 'sls']:
                                if sum(trades[i[0]][j]['percent']) != 100:
                                    trades[i[0]][j]['point'].append(i[4+offset])
                                    trades[i[0]][j]['percent'].append(i[5+offset])
                                    trades[i[0]][j]['filled'].append(i[6+offset])
                                offset += 3

                    price = float(msg.get('c'))
                    # store decimals for price
                    last_f_digits = int(str(price)[::-1].find('.'))

                    if last_f_digits > f_digits:
                        f_digits = last_f_digits

                    for trade in trades:
                        for target_type in ['entries', 'tps', 'sls']:
                            for i in range(len(trades[trade][target_type]['point'])):
                                
                                if not trades[trade][target_type]['filled'][i]:
                                    point = trades[trade][target_type]['point'][i]
                                    point = float(f"{str(point).split('.')[0]}.{str(point).split('.')[1][:f_digits]}")
                                    if trades[trade]['direction'] == 'long':                 
                                        if target_type == 'entries' and price == point:
                                            message = f'Entry target {i+1} reached, {trades[trade]["symbol"]}'
                                            cur.execute(
                                                f'''
                                                UPDATE entries
                                                SET filled = True
                                                WHERE trade_id = '{trade}' and price = '{trades[trade][target_type]['point'][i]}';
                                                '''
                                            )
                                            conn.commit()
                                            print(message)
                                            bot.send_message(
                                                chat_id = trades[trade].get('telegram_channel_id'),
                                                text = message,
                                                reply_to_message_id = trades[trade].get('telegram_message_id')
                                            )

                                        elif target_type == 'tps' and price == point:
                                            message = f'TP target {i+1} reached, {trades[trade]["symbol"]}'
                                            cur.execute(
                                                f'''
                                                UPDATE tps
                                                SET filled = True
                                                WHERE trade_id = '{trade}' and price = '{trades[trade][target_type]['point'][i]}';
                                                '''
                                            )
                                            conn.commit()
                                            print(message)
                                            bot.send_message(
                                                chat_id = trades[trade].get('telegram_channel_id'),
                                                text = message,
                                                reply_to_message_id = trades[trade].get('telegram_message_id')
                                            )

                                        elif target_type == 'sls' and price == point:
                                            message = f'TP target {i+1} reached, {trades[trade]["symbol"]}'
                                            cur.execute(
                                                f'''
                                                UPDATE sls
                                                SET filled = True
                                                WHERE trade_id = '{trade}' and price = '{trades[trade][target_type]['point'][i]}';
                                                '''
                                            )
                                            conn.commit()
                                            print(message)
                                            bot.send_message(
                                                chat_id = trades[trade].get('telegram_channel_id'),
                                                text = message,
                                                reply_to_message_id = trades[trade].get('telegram_message_id')
                                            )

                                    elif trades[trade]['direction'] == 'short':
                                        if target_type == 'entries' and price != point:
                                            message = f'Entry target {i+1} reached, {trades[trade]["symbol"]}'
                                            cur.execute(
                                                f'''
                                                UPDATE entries
                                                SET filled = True
                                                WHERE trade_id = '{trade}' and price = '{trades[trade][target_type]['point'][i]}';
                                                '''
                                            )
                                            conn.commit()
                                            print(message)
                                            bot.send_message(
                                                chat_id = trades[trade].get('telegram_channel_id'),
                                                text = message,
                                                reply_to_message_id = trades[trade].get('telegram_message_id')
                                            )

                                        elif target_type == 'tps' and price == point:
                                            message = f'TP target {i+1} reached, {trades[trade]["symbol"]}'
                                            cur.execute(
                                                f'''
                                                UPDATE tps
                                                SET filled = True
                                                WHERE trade_id = '{trade}' and price = '{trades[trade][target_type]['point'][i]}';
                                                '''
                                            )
                                            conn.commit()
                                            print(message)
                                            bot.send_message(
                                                chat_id = trades[trade].get('telegram_channel_id'),
                                                text = message,
                                                reply_to_message_id = trades[trade].get('telegram_message_id')
                                            )

                                        elif target_type == 'sls' and price == point:
                                            message = f'TP target {i+1} reached, {trades[trade]["symbol"]}'
                                            cur.execute(
                                                f'''
                                                UPDATE sls
                                                SET filled = True
                                                WHERE trade_id = '{trade}' and price = '{trades[trade][target_type]['point'][i]}';
                                                '''
                                            )
                                            conn.commit()
                                            print(message)
                                            bot.send_message(
                                                chat_id = trades[trade].get('telegram_channel_id'),
                                                text = message,
                                                reply_to_message_id = trades[trade].get('telegram_message_id')
                                            )
                    
                    cur.close()
                    pool.putconn(conn)
                
    def start(self, pool, symbol, bot):
        if self.exchange == 'binance.com' or self.exchange == 'binance.com-futures':
            self.user_data_stream = self.binance_websocket.create_stream(self.stream, self.coin, output='dict')
            self.worker_thread = threading.Thread(target=self.handle_market_data_stream, args=(self.binance_websocket, pool, symbol, bot))
            self.worker_thread.start()
            return self.user_data_stream

    def stop(self, stream):
        if self.exchange == 'binance.com' or self.exchange == 'binance.com-futures':
            self.binance_websocket.stop_stream(stream)