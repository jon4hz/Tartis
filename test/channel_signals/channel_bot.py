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
    InlineKeyboardButton
)
# import tartis
import tartis
# other
import sys, logging, os, sqlite3, json

logging.basicConfig(level=logging.INFO,
                    filename=os.path.basename(__file__) + '.log',
                    format="{asctime} [{levelname:8}] {process} {thread} {module}: {message}",
                    style="{")

#==================================================================================================
# CONSTANTS
#==================================================================================================

DATABASE_FILE = 'database.db'

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

    print('Start Tartis initialization...')

    if not bot_initialized:

        # remove old uuids from past streams
        if 'market_data_stream' in context.bot_data.keys():
            context.bot_data['market_data_stream'].clear()
        else:
            context.bot_data['market_data_stream'] = {}

        if context.bot_data.get('market_data'):
            for i in context.bot_data.get('market_data'):
                if context.bot_data['market_data'].get(i):
                    stream = tartis.market_data('binance.com-futures', 'miniTicker', i, DATABASE_FILE).start()
                    context.bot_data['market_data_stream'][i] = str(stream)

        # create database for trades
        # database
        con = sqlite3.connect(DATABASE_FILE)
        cur = con.cursor()
        cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS trades(
            id integer PRIMARY KEY,
            symbol string,
            exchange string,
            open_time int,
            close_time int,
            entry_filled integer,
            entry_1 string,
            entry_2 string,
            entry_3 string,
            entry_4 string,
            entry_5 string,
            entry_6 string,
            entry_7 string,
            entry_8 string,
            entry_9 string,
            entry_10 string,
            tp_1 string,
            tp_2 string,
            tp_3 string,
            tp_4 string,
            tp_5 string,
            tp_6 string,
            tp_7 string,
            tp_8 string,
            tp_9 string,
            tp_10 string,
            sl_1 string,
            sl_2 string,
            sl_3 string,
            sl_4 string,
            sl_5 string,
            sl_6 string,
            sl_7 string,
            sl_8 string,
            sl_9 string,
            sl_10 string,
            entry_1_filled string,
            entry_2_filled string,
            entry_3_filled string,
            entry_4_filled string,
            entry_5_filled string,
            entry_6_filled string,
            entry_7_filled string,
            entry_8_filled string,
            entry_9_filled string,
            entry_10_filled string,
            tp_1_filled string,
            tp_2_filled string,
            tp_3_filled string,
            tp_4_filled string,
            tp_5_filled string,
            tp_6_filled string,
            tp_7_filled string,
            tp_8_filled string,
            tp_9_filled string,
            tp_10_filled string,
            sl_1_filled string,
            sl_2_filled string,
            sl_3_filled string,
            sl_4_filled string,
            sl_5_filled string,
            sl_6_filled string,
            sl_7_filled string,
            sl_8_filled string,
            sl_9_filled string,
            sl_10_filled string
        )
        ''')
    con.commit()
    con.close()

    bot_initialized = True
    print('Initialization complete!')
    

def get_message(update, context):
    if bot_initialized:
        x = update.effective_message.text
        if '/' in x:
            x = ''.join(x.split('/'))

        if 'market_data' in context.bot_data.keys():
            if x not in context.bot_data['market_data']:
                stream = tartis.market_data('binance.com-futures', 'miniTicker', x, DATABASE_FILE).start()
                context.bot_data['market_data'][x] = True
                context.bot_data['market_data_stream'][x] = str(stream)
        else:
            context.bot_data['market_data'] = {x: True}
            stream = tartis.market_data('binance.com-futures', 'miniTicker', x, DATABASE_FILE).start()
            context.bot_data['market_data_stream'] = {x: str(stream)}
    

        
#==================================================================================================
# MAIN
#==================================================================================================

# Tartis
message_parser = tartis.messageParser()

# Telegram
defaults = Defaults(parse_mode=ParseMode.HTML)
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