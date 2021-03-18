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
import sys, logging

logging.basicConfig(level=logging.INFO,
                    format="{asctime} [{levelname:8}] {process} {thread} {module}: {message}",
                    style="{")

#==================================================================================================
# TELEGRAM FUNCTIONS
#==================================================================================================

def start(update, context):
    print(context.bot_data)
    

def start_websocket(update, context):
    x = update.effective_message.text
    if '/' in x:
        x = ''.join(x.split('/'))
    tartis.websocket('binance.com', 'miniTicker', x).start()
    if 'market_data' in context.bot_data.keys():
        context.bot_data['market_data'].append(x)
    else:
        context.bot_data['market_data'] = [x]

        
#==================================================================================================
# MAIN
#==================================================================================================

# Telegram
defaults = Defaults(parse_mode=ParseMode.HTML)
pp = PicklePersistence(filename='persitenceBot.pickle', single_file=False)
updater = Updater(TOKEN, use_context=True, persistence=pp, defaults=defaults)
dp = updater.dispatcher

dp.add_handler(
    CommandHandler('start', start)
)

dp.add_handler(
    MessageHandler(Filters.text, start_websocket)
)

updater.start_polling()
updater.idle()