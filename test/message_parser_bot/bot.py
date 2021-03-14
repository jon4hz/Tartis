#!/usr/bin/python3.8
# 
# Author: jon4hz
# Date: 10.03.2021
# Desc: Telegram Bot which validates signals and returns the output
#
#####################################################################################################################################################

# import Bot Token
from config import TOKEN
# import python-telegram-bot modules
from telegram.ext import (
    Updater,
    MessageHandler,
    CommandHandler,
    Defaults,
    Filters
)
from telegram import (
    ParseMode
)
# import tartis
import tartis
# other
import sys

#==================================================================================================
# BOT FUNCTIONS
#==================================================================================================

def welcome(update, context):
    context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = 'Welcome! This is a live test for the message parser of <a href="github.com/jon4hz/tartis">tartis</a> \nJust send a Signal to the bot and it will try to interpret it as a trading signal.'
    )

def message_handler(update, context):
    try:
        x = message_parser.parse_message(update.message.text)
        string = f'{x["pair"]}:\n'
        for t in ['entry', 'tp', 'sl']:
            string += f'{t.upper()}1-X:\n'
            for j in range(len(x[t]['point'])):
                string += f"{x[t]['point'][j]} - {x[t]['percent'][j]}%\n"
        context.bot.send_message(
            chat_id = update.effective_chat.id,
            text = string
        )
    except Exception as e:
        context.bot.send_message(
            chat_id = update.effective_chat.id,
            text = f'Error - {type(e).__name__}, {__file__}, {e.__traceback__.tb_lineno}, {e}'
        )
    """ x = message_parser.parse_message(update.message.text)
    string = f'{x["pair"]}:\n'
    for t in ['entry', 'tp', 'sl']:
        string += f'{t.upper()}1-X:\n'
        for j in range(len(x[t]['point'])):
            string += f"{x[t]['point'][j]} - {x[t]['percent'][j]}%\n"
    context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = string
    ) """
#==================================================================================================
# MAIN
#==================================================================================================

# Create Tartis Message Parser
message_parser = tartis.utils.messageParser()

# Telegram
defaults = Defaults(parse_mode=ParseMode.HTML)
updater = Updater(TOKEN, use_context=True, defaults=defaults)
dp = updater.dispatcher

dp.add_handler(
    CommandHandler('start', welcome)
)

dp.add_handler(
    MessageHandler(Filters.text, message_handler)
)

updater.start_polling()
updater.idle()