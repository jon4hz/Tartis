#!/usr/bin/python3.8
# 
# Author: jon4hz
# Date: 10.03.2021
# Desc: Telegram Bot which validates signals and returns the output
#
#####################################################################################################################################################

# import configs
from config import (
    TOKEN, 
    ADMIN_CHANNEL
)
# import python-telegram-bot modules
from telegram.ext import (
    Updater,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    Defaults,
    Filters
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
# BOT FUNCTIONS
#==================================================================================================

def welcome(update, context):
    context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = 'Welcome! This is a live test for the message parser of <a href="github.com/jon4hz/tartis">tartis</a> \nJust send a Signal to the bot and it will try to interpret it as a trading signal.'
    )

def message_handler(update, context):
    try:
        x = message_parser.parse_message(update.effective_message.text)
        string = f'{x["pair"]}:\n'
        for t in ['entry', 'tp', 'sl']:
            string += f'{t.upper()}1-X:\n'
            for j in range(len(x[t]['point'])):
                string += f"{x[t]['point'][j]} - {x[t]['percent'][j]}%\n"
        context.bot.send_message(
            chat_id = update.effective_chat.id,
            text = string,
            reply_to_message_id = update.message.message_id,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("👍", callback_data="ok"),
                InlineKeyboardButton("👎", callback_data="nok")]
        ])
        )
    except Exception as e:
        context.bot.send_message(
            chat_id = update.effective_chat.id,
            text = f'Error - {type(e).__name__}, {__file__}, {e.__traceback__.tb_lineno}, {e}'
        )
        context.bot.send_message(
            chat_id = ADMIN_CHANNEL,
            text = update.effective_message.text
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

def parsing_feedback(update, context):
    if update.callback_query.data == 'ok':
        context.bot.edit_message_text(
            chat_id = update.effective_chat.id,
            message_id = update.callback_query.message.message_id,
            text = update.effective_message.text,
            reply_markup = None
        )
        context.bot.answer_callback_query(
            callback_query_id = update.callback_query.id,
            text = 'Nice 🥳'
        )

    elif update.callback_query.data == 'nok':
        context.bot.edit_message_text(
            chat_id = update.effective_chat.id,
            message_id = update.callback_query.message.message_id,
            text = update.effective_message.text,
            reply_markup = None
        )
        context.bot.answer_callback_query(
            callback_query_id = update.callback_query.id,
            text = 'Mistake reported 🤓'
        )
        context.bot.forward_message(
            chat_id = ADMIN_CHANNEL,
            from_chat_id = update.effective_chat.id,
            message_id = update.callback_query.message.reply_to_message.message_id
        )

#==================================================================================================
# MAIN
#==================================================================================================

# Create Tartis Message Parser
message_parser = tartis.messageParser()

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
dp.add_handler(
    CallbackQueryHandler(parsing_feedback, pattern=r"(ok|nok)")
)

updater.start_polling()
updater.idle()