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
import sys

#==================================================================================================
# TELEGRAM FUNCTIONS
#==================================================================================================

def start(update, context):
    print(1)
    print(context.bot_data)
    

def start_websocket(update, context):
    x = update.effective_message.text
    if '/' in x:
        x = ''.join(x.split('/'))
    context.bot_data[x] = tartis.websocket('binance.com', 'miniTicker', x).start()
#==================================================================================================
# MAIN
#==================================================================================================

# Telegram
defaults = Defaults(parse_mode=ParseMode.HTML)
pp = PicklePersistence(filename='persitenceBot.pickle', store_bot_data=True)
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