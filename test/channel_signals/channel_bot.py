#!/usr/bin/python3.8
# 
# Author: jon4hz
# Date: 10.03.2021
# Desc: Tartis Trading Bot
#
#####################################################################################################################################################
# import configs
from config import (
    TOKEN
)
# import python-telegram-bot modules
from telegram.ext import (
    Updater,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    Defaults,
    Filters,
    PicklePersistence
)
from telegram import (
    ParseMode,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Bot
)
# import tartis
import tartis
# other
import sys, logging, os, psycopg2, json, datetime
from psycopg2.pool import ThreadedConnectionPool

logging.basicConfig(level=logging.INFO,
                    filename=os.path.basename(__file__) + '.log',
                    format="{asctime} [{levelname:8}] {process} {thread} {module}: {message}",
                    style="{")

#==================================================================================================
# CONSTANTS
#==================================================================================================



#==================================================================================================
# VARIABLES
#==================================================================================================

bot_initialized = False

#==================================================================================================
# TELEGRAM FUNCTIONS
#==================================================================================================

def start(update, context):
    print(context.bot_data)

def init(update, context):
    global bot_initialized

    if not bot_initialized:
        print('Starting Tartis initialization...')

        # create database for trades
        # database
        conn = dbpool.getconn()
        cur = conn.cursor()
        statements = ['''
        CREATE TABLE IF NOT EXISTS trades
        (
            id            bigserial,
            symbol        varchar(15) NOT NULL,
            direction     varchar(5)  NOT NULL,
            exchange      varchar(50),
            open_time     integer    ,
            close_time    integer    ,
            channel_trade boolean    ,
            telegram_message_id bigint,
            PRIMARY KEY (id)
        );
        ''',
        '''
        CREATE TABLE IF NOT EXISTS entries
        (
            id       bigserial,
            trade_id bigserial  NOT NULL,
            price    decimal NOT NULL,
            percent  decimal,
            quantity decimal,
            filled   boolean,
            PRIMARY KEY (id),
            CONSTRAINT FK_trades_TO_entries
                FOREIGN KEY (trade_id)
                REFERENCES trades (id)
        );''',
        '''
        CREATE TABLE IF NOT EXISTS sls
        (
            id       bigserial,
            trade_id bigserial NOT NULL,
            price    decimal NOT NULL,
            percent  decimal,
            quantity decimal,
            filled   boolean,
            PRIMARY KEY (id),
            CONSTRAINT FK_trades_TO_sls
                FOREIGN KEY (trade_id)
                REFERENCES trades (id)
        );
        ''',
        '''
        CREATE TABLE IF NOT EXISTS tps
        (
            id       bigserial,
            trade_id bigserial  NOT NULL,
            price    decimal NOT NULL,
            percent  decimal,
            quantity decimal,
            filled   boolean,
            PRIMARY KEY (id),
            CONSTRAINT FK_trades_TO_tps
                FOREIGN KEY (trade_id)
                REFERENCES trades (id)
        );  
        ''']
        for statement in statements:
            cur.execute(statement)
        conn.commit()
        dbpool.putconn(conn)

        # remove old uuids from past streams
        if 'market_data_stream' in context.bot_data.keys():
            context.bot_data['market_data_stream'].clear()
        else:
            context.bot_data['market_data_stream'] = {}

        if context.bot_data.get('market_data'):
            for i in context.bot_data.get('market_data'):
                if context.bot_data['market_data'].get(i):
                    j = ''.join(i.split('/'))
                    stream = tartis.market_data('binance.com-futures', 'miniTicker', j).start(dbpool, i, bot)
                    context.bot_data['market_data_stream'][i] = str(stream)

        bot_initialized = True
        print('Initialization complete!')
    else:
        print('Bot already initialized. Nothing to do...')
    

def get_message(update, context):
    if bot_initialized:
        signal = message_parser.parse_message(update.effective_message.text)
        print(signal)

        # get direction
        if float(signal['entry']['point'][0]) < float(signal['tp']['point'][0]):
            direction = 'long'
        else:
            direction = 'short'

        # set exchange
        exchange = 'binance'

        conn = dbpool.getconn()
        cur = conn.cursor()
        cur.execute(
            f'''
            INSERT INTO trades(
                symbol,
                direction,
                exchange,
                open_time,
                channel_trade,
                telegram_message_id
            ) VALUES (
                '{signal['pair']}',
                '{direction}',
                '{exchange}',
                '{int(datetime.datetime.utcnow().timestamp())}',
                True,
                '{update.message.message_id}'
            ) RETURNING id
            '''
        )
        
        pk = cur.fetchone()[0]

        for i in range(len(signal['entry']['point'])):
            cur.execute(
                f'''
                INSERT INTO entries(
                    price,
                    percent,
                    trade_id
                ) VALUES (
                    '{signal['entry']['point'][i]}',
                    '{signal['entry']['percent'][i]}',
                    '{pk}'
                )
                '''
            )

        for i in range(len(signal['tp']['point'])):
            cur.execute(
                f'''
                INSERT INTO tps(
                    price,
                    percent,
                    trade_id
                ) VALUES (
                    '{signal['tp']['point'][i]}',
                    '{signal['tp']['percent'][i]}',
                    '{pk}'
                )
                '''
            )

        for i in range(len(signal['sl']['point'])):
            cur.execute(
                f'''
                INSERT INTO sls(
                    price,
                    percent,
                    trade_id
                ) VALUES (
                    '{signal['sl']['point'][i]}',
                    '{signal['sl']['percent'][i]}',
                    '{pk}'
                )
                '''
            )
        
        conn.commit()
        cur.close()
        dbpool.putconn(conn)
        # start market websocket for symbol
        symbol = ''.join(signal['pair'].split('/'))

        if 'market_data' in context.bot_data.keys():
            if symbol not in context.bot_data['market_data']:
                stream = tartis.market_data('binance.com-futures', 'miniTicker', symbol).start(dbpool, signal['pair'], bot)
                context.bot_data['market_data'][signal['pair']] = True
                context.bot_data['market_data_stream'][signal['pair']] = str(stream)
        else:
            context.bot_data['market_data'] = {signal['pair']: True}
            stream = tartis.market_data('binance.com-futures', 'miniTicker', symbol).start(dbpool, signal['pair'], bot)
            context.bot_data['market_data_stream'] = {signal['pair']: str(stream)}

#==================================================================================================
# MAIN
#==================================================================================================

# Tartis
message_parser = tartis.messageParser()

# database
dbpool = ThreadedConnectionPool(
    1, 
    100,
    dbname = 'tartis',
    host = 'localhost',
    port = '5432',
    user = 'tartis',
    password = 'tmppassword'
)

# Telegram
defaults = Defaults(parse_mode=ParseMode.HTML)
bot = Bot(TOKEN)
pp = PicklePersistence(filename='persitenceBot.pickle', single_file=True)
updater = Updater(TOKEN, use_context=True, persistence=pp, defaults=defaults)
dp = updater.dispatcher

dp.add_handler(
    CommandHandler('start', start)
)

dp.add_handler(
    CommandHandler('init', init)
)

dp.add_handler(
    MessageHandler(Filters.text, get_message)
)

updater.start_polling()
updater.idle()